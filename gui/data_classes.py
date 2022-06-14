import dataclasses
import enum
import numpy as np


@dataclasses.dataclass
class Frame:
    cv_img: np.ndarray
    cam_index: int

class CameraType(enum.Enum):
    FRONT = 'front'
    BACK = 'back'
    BOTTOM = 'bottom'
    DUAL = 'dual'

@dataclasses.dataclass
class VideoSource:
    filename: str
    api_preference: int
    width: int
    height: int
