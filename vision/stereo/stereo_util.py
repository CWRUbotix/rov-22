from enum import Enum

import numpy as np


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