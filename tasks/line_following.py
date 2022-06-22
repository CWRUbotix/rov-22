import math
import numpy as np
import time
import cv2

from gui.data_classes import Frame
from tasks.base_task import BaseTask
from vehicle.vehicle_control import VehicleControl, InputChannel
from logger import root_logger

logger = root_logger.getChild(__name__)

TRANSLATION_SENSITIVITY = 0.45
ROTATIONAL_SENSITIVITY = 0.55

MAX_TASK_DURATION = 500
MIN_TASK_DURATION = 2

DO_PRINTING = True
DO_LOGGING = True

CRAWL_SPEED = 0.4
RAM_SPEED = 0.9

START_WIDTH_FRACTION = 1
START_HEIGHT_FRACTION = 0.035

STOP_WIDTH_FRACTION = 1
STOP_HEIGHT_FRACTION = 0.15

END_WIDTH_FRACTION = 0.3
END_HEIGHT_FRACTION = 0.3

def get_line_contour(cv_img):
    h, w, _ = cv_img.shape
    cv_img = cv_img[:,int(w/2):w]
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

    lower = np.array([155, 25, 0])
    upper = np.array([179, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    masked = cv2.cvtClor(cv2.bitwise_and(hsv, hsv, mask=mask), cv2.COLOR_HSV2BGR)

    grey = masked[:, :, 2]
    height, width = grey.shape

    ret, thresh = cv2.threshold(grey, 0, 255, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    best_contour = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < width and h < height and w * h > high_score:
            high_score = w * h
            best_contour = contour
    print(high_score)
    return best_contour, high_score

class LineFollowing(BaseTask):

    def __init__(self, vehicle: VehicleControl):
        super().__init__(vehicle)
        self.line_pos = [-1, -1]
        self.line_dims = [-1, -1] #make horizontal
        self.image_dims = [-1, -1]
        self.start_time = 0

        self.state = 0

    def initialize(self):
        self.vehicle.stop_thrusters()
        self.start_time = time.time()

        self.vehicle.set_mode("ALT_HOLD") #is this a mapping?
        self.state = 0

        if DO_LOGGING: logger.debug('Line Following: RIGHT')
        if DO_PRINTING: print('Line Following: RIGHT')

    def periodic(self):
        if self.line_pos == [-1, -1]:
            return
        
        scale = max(-math.log(self.button_dims[0] / self.image_dims[0]) / 10, 0.1)

        if self.state == 0:
            if self.button_dims[0] >= START_WIDTH_FRACTION * self.image_dims[0] or self.line_dims[1] >= START_HEIGHT_FRACTION * self.image_dims[1]:
                self.state = 1
                self.vehicle.set_mode("MANUAL")
                if DO_LOGGING: logger.debug('Line Following: CHANGE')
                if DO_PRINTING: print('Line Following: CHANGE')

                inputs = {
                    InputChannel.FORWARD: CRAWL_SPEED,
                    InputChannel.LATERAL: 0,
                    InputChannel.THROTTLE: 0,
                }

