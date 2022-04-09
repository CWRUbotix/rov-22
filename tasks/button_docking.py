import numpy as np
import time
from PyQt5.QtCore import Qt
import cv2
from gui.data_classes import Frame
from tasks.base_task import BaseTask
from vehicle.vehicle_control import VehicleControl, InputChannel

TRANSLATION_SENSITIVITY = 0.2
ROTATIONAL_SENSITIVITY = 1.0
FORWARD_SPEED = 0.05

MAX_TASK_DURATION = 500
MIN_TASK_DURATION = 2

# The fraction of the screen that the button takes up when we've gotten close enough to it
STOP_WIDTH_FRACTION = 0.3
STOP_HEIGHT_FRACTION = 0.3


def get_button_contour(cv_img):
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

    # Mask out non-red stuff
    lower = np.array([155,25,0])
    upper = np.array([179,255,255])
    mask = cv2.inRange(hsv, lower, upper)
    masked = cv2.cvtColor(cv2.bitwise_and(hsv, hsv, mask=mask), cv2.COLOR_HSV2BGR)

    # Get grayscale of red channel
    gray = masked[:,:,2]
    height, width = gray.shape  # calling this on the BGR will get (x, y, 3)

    # Threshold it for a bitmap around redest stuff
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find the largest contour
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    high_score = 0
    best_contour = None
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        if w < width and h < height and w * h > high_score:
            high_score = w * h
            best_contour = contour
    
    return (best_contour, high_score)


class ButtonDocking(BaseTask):
    """
    Fly forward, strafing/rotating to aim at large splotches of red, until:
        - the red fills a fixed amount of the frame or
        - a fixed amount of time passes
    """
    def __init__(self, vehicle: VehicleControl):
        super().__init__(vehicle)
        self.button_pos = [-1, -1]
        self.button_dims = [-1,-1]
        self.image_dims = [-1, -1]
        self.start_time = 0

    def initialize(self):
        self.vehicle.stop_thrusters()
        self.start_time = time.time()

    def periodic(self):
        """Drive forward in the directions indicated by the vertical_move and horizontal_move methods"""
        if self.button_pos != [-1, -1]:
            inputs = {
                InputChannel.FORWARD:  FORWARD_SPEED,
                InputChannel.LATERAL:  0,
                InputChannel.THROTTLE: self.vertical_move() * TRANSLATION_SENSITIVITY,
                InputChannel.PITCH:    self.vertical_move() * ROTATIONAL_SENSITIVITY,
                InputChannel.YAW:      self.horizontal_move() * ROTATIONAL_SENSITIVITY,
                InputChannel.ROLL:     0,
            }

            self.vehicle.set_rc_inputs(inputs)
    
    def horizontal_move(self):
        """Return the change in yaw that will aim us at the button, in [-1,1]"""
        return (self.button_pos[0] - self.image_dims[0] / 2) / (self.image_dims[0] / 2)
    
    def vertical_move(self):
        """Return the change in pitch that will aim us at the button, in [-1,1]"""
        # need to negate b/c inverted y axis
        return -1 * (self.button_pos[1] - self.image_dims[1] / 2) / (self.image_dims[1] / 2)
    
    def handle_frame(self, frame: Frame):
        """Recalculate button position info if possible whenever a new frame is recieved"""
        best_contour, high_score = get_button_contour(frame.cv_img)
        
        # Calculate button position info if we found a good countour
        if high_score > 0:
            x,y,w,h = cv2.boundingRect(best_contour)
            self.button_pos = [x + w/2, y + h/2]
            self.button_dims = [w, h]
            height, width, colors = frame.cv_img.shape
            self.image_dims = [width, height]
        
    def is_finished(self) -> bool:
        """
        Stops the task if we've spent at least some time looking around
        and (we've hit the button or exceeded max task time)
        """
        return  time.time() >= self.start_time + MIN_TASK_DURATION and \
                (self.button_dims[0] > STOP_WIDTH_FRACTION * self.image_dims[0] or \
                self.button_dims[1] > STOP_HEIGHT_FRACTION * self.image_dims[1] or \
                time.time() >= self.start_time + MAX_TASK_DURATION)

    def end(self):
        self.vehicle.stop_thrusters()