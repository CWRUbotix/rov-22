from os import path
from vision.stereo.fish_features import refine_coords, vertical_edge
from vision.stereo.stereo_util import Side
from vision.stereo.params import StereoParameters
import numpy as np
import cv2

from util import data_path


class PixelSelector:

    # The number of pixels that are displayed on screen
    WIN_SIZE = 600

    # How many pixels in original image space are contained in the view. This defines the zoom level.
    view_size = 300
    # Coordinates of the top-left pixel in original image space where the view starts
    view_xl = 0
    view_xr = 0
    view_y = 0

    dragging = False
    drag_side = None
    # Coordinates of mouse at beginning of drag
    drag_mouse_x = 0
    drag_mouse_y = 0
    # Coordinates of view at beginning of drag
    drag_view_x = 0
    drag_view_y = 0

    target_xl = 50
    target_xr = 50
    target_y = 50

    def __init__(self, img_l: np.ndarray, img_r: np.ndarray, params: StereoParameters):
        self.img_l = params.rectify_single(img_l, Side.LEFT)
        self.img_r = params.rectify_single(img_r, Side.RIGHT)

        self.img_l = cv2.GaussianBlur(self.img_l, (15, 15), 0)
        self.img_r = cv2.GaussianBlur(self.img_r, (15, 15), 0)

        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        kernel = np.array([[0, 0, 0], [-1, 0, 1], [0, 0, 0]])

        #kernel = np.array([[1, 4, 6, 4, 1], [4, 16, 24, 16, 4], [6, 24, -476, 24, 6], [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]]) / -256
        # self.img_l = vertical_edge(self.img_l)
        # self.img_l = cv2.cvtColor(self.img_l, cv2.COLOR_GRAY2BGR)

        self.img_width = self.img_l.shape[1]
        self.img_height = self.img_l.shape[0]

        cv2.namedWindow('Pixels')
        cv2.setMouseCallback('Pixels', self.mouse_callback)
    
    def run(self):
        while True:
            img_l = self._draw_crosshairs(self.img_l, self.target_xl, self.target_y)
            img_r = self._draw_crosshairs(self.img_r, self.target_xr, self.target_y)
            
            crop_l = img_l[self.view_y : self.view_y + self.view_size, self.view_xl : self.view_xl + self.view_size]
            resized_l = cv2.resize(crop_l, (self.WIN_SIZE, self.WIN_SIZE), interpolation=cv2.INTER_CUBIC)

            crop_r = img_r[self.view_y : self.view_y + self.view_size, self.view_xr : self.view_xr + self.view_size]
            resized_r = cv2.resize(crop_r, (self.WIN_SIZE, self.WIN_SIZE), interpolation=cv2.INTER_CUBIC)

            resized = np.concatenate((resized_l, resized_r), axis=1)
            cv2.imshow('Pixels', resized)

            key = cv2.waitKey(20) & 0xFF

            if key == ord('x'):
                if self.view_size > 100:
                    self.view_size = int(self.view_size / 2)
            elif key == ord('z'):
                if  2 * self.view_size <= min(self.img_width, self.img_height):
                    self.view_size *= 2
                    self._clamp_view()
            elif key == ord('f'):
                # vals = self.img_l[ self.target_y, self.target_xl - 9 : self.target_xl + 10, 0]
                # print(vals)
                return self.target_xl, self.target_xr, self.target_y
            elif key == ord('r'):
                self.target_xl, self.target_xr, self.target_y = refine_coords(self.img_l, self.img_r, self.target_xl, self.target_xr, self.target_y)
            elif key == 27:
                break
    
    def _draw_crosshairs(self, img, x, y):
        img = img.copy()
        cv2.line(img, (x, 0), (x, self.img_height), (0, 0, 255), thickness=1)
        cv2.line(img, (0, y), (self.img_width, y), (0, 0, 255), thickness=1)
        return img
    
    def mouse_callback(self, event, x, y, flags, param):
        side = Side.LEFT if x < self.WIN_SIZE else Side.RIGHT
        multiplier = self.view_size / self.WIN_SIZE

        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.drag_side = side
            self.drag_mouse_x = x
            self.drag_mouse_y = y
            self.drag_view_x = self.view_xl if side == Side.LEFT else self.view_xr
            self.drag_view_y = self.view_y

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging:
                delta_x = int(multiplier * (self.drag_mouse_x - x))
                delta_y = int(multiplier * (self.drag_mouse_y - y))
                if self.drag_side == Side.LEFT:
                    self.view_xl = self.drag_view_x + delta_x
                else:
                    self.view_xr = self.drag_view_x + delta_x
                self.view_y = self.drag_view_y + delta_y
                self._clamp_view()
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            if side == Side.LEFT:
                self.target_xl = int(self.view_xl + multiplier * x)
            else:
                self.target_xr = int(self.view_xr + multiplier * (x - self.WIN_SIZE))
            
            self.target_y = int(self.view_y + multiplier * y)
    
    def _clamp_view(self):
        if self.view_xl < 0:
            self.view_xl = 0
        if self.view_xl + self.view_size > self.img_width:
            self.view_xl = self.img_width - self.view_size

        if self.view_xr < 0:
            self.view_xr = 0
        if self.view_xr + self.view_size > self.img_width:
            self.view_xr = self.img_width - self.view_size
        
        if self.view_y < 0:
            self.view_y = 0
        if self.view_y + self.view_size > self.img_height:
            self.view_y = self.img_height - self.view_size


if __name__ == '__main__':
    params = StereoParameters.load('stereo')
    img_l = cv2.imread(path.join(data_path, 'stereo', 'dualcam1', 'left', '2.png'))
    img_r = cv2.imread(path.join(data_path, 'stereo', 'dualcam1', 'right', '2.png'))
    img = np.concatenate((img_l, img_r), axis=1)

    p = PixelSelector(img_l, img_r, params=params)
    p.run()