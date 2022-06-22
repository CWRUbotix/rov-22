from enum import Enum
import dataclasses

import numpy as np
import cv2


class Side(Enum):
    LEFT = 1
    RIGHT = 2

def left_half(img: np.ndarray) -> np.ndarray:
    width = img.shape[1]
    half = int(width / 2)
    return img[:, 0:half]

def right_half(img: np.ndarray) -> np.ndarray:
    width = img.shape[1]
    half = int(width / 2)
    return img[:, half:width]

def draw_crosshairs(img: np.ndarray, x: int, y: int, color=(0, 0, 255), thickness=1):
    height, width, _ = img.shape
    img = img.copy()
    cv2.line(img, (x, 0), (x, height), color, thickness=thickness)
    cv2.line(img, (0, y), (width, y), color, thickness=thickness)
    return img

@dataclasses.dataclass
class StereoCoordinate:
    xl: int
    xr: int
    y: int

    def triangulate(self, params):
        point_l = np.array([[self.xl], [self.y]], dtype=np.float64)
        point_r = np.array([[self.xr], [self.y]], dtype=np.float64)
        return params.triangulate(point_l, point_r)

    def __iter__(self):
        return StereoCoordinate.Iterator(self)

    class Iterator:

        def __init__(self, stereo_coordinate):
            self.stereo_coordinate = stereo_coordinate
            self.idx = 0
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if self.idx >=3:
                raise StopIteration()
            elif self.idx == 0:
                ret = self.stereo_coordinate.xl
            elif self.idx == 1:
                ret = self.stereo_coordinate.xr
            else:
                ret = self.stereo_coordinate.y
            
            self.idx += 1
            return ret