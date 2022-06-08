import dataclasses
import enum
import numpy as np


@dataclasses.dataclass
class Frame:
    cv_img: np.ndarray
    cam_index: int

class CameraAngle(enum.Enum):
    FRONT = 'front'
    BACK = 'back'
    BOTTOM = 'bottom'
    NONE = 'none'

@dataclasses.dataclass
class VideoSource:
    filename: str
    api_preference: int
