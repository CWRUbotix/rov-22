import dataclasses
import numpy as np


@dataclasses.dataclass
class Frame:
    cv_img: np.ndarray
    cam_index: int
