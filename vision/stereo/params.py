from enum import Enum
import pickle
from dataclasses import dataclass
from typing import Tuple
from vision.stereo.stereo_util import Side, left_half, right_half
import numpy as np
from os import path

import cv2

from util import config_path

@dataclass(frozen=True)
class StereoParameters:
    proj_l: np.ndarray
    proj_r: np.ndarray
    left_rectify_map: Tuple[np.ndarray, np.ndarray]
    right_rectify_map: Tuple[np.ndarray, np.ndarray]

    def rectify_single(self, img: np.ndarray, side: Side):
        map = self.left_rectify_map if side == Side.LEFT else self.right_rectify_map
        return cv2.remap(img, map[0], map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

    def rectify_stereo(self, img: np.ndarray):
        left = self.rectify_single(left_half(img), Side.LEFT)
        right = self.rectify_single(right_half(img), Side.RIGHT)
        return np.concatenate((left, right), axis=1)
    
    def triangulate_stereo_coord(self, point):
        point_l = np.array([[point.xl], [point.y]], dtype=np.float64)
        point_r = np.array([[point.xr], [point.y]], dtype=np.float64)
        triangulated = cv2.triangulatePoints(self.proj_l, self.proj_r, point_l, point_r).reshape(4)
        print(triangulated)
        triangulated /= triangulated[3]
        return triangulated[0:3]

    def triangulate(self, point_l, point_r):
        point = cv2.triangulatePoints(self.proj_l, self.proj_r, point_l, point_r).reshape(4)
        point /= point[3]
        return point[0:3]


    @staticmethod
    def _file_path(name: str):
        return path.join(config_path, 'stereo', name + '.pickle')

    def save(self, name: str):
        with open(StereoParameters._file_path(name), 'ba') as file:
            pickle.dump(self, file)
    
    @staticmethod
    def load(name: str) -> 'StereoParameters':
        with open(StereoParameters._file_path(name), 'rb') as file:
            params = pickle.load(file)
        return params


if __name__ == '__main__':
    p = StereoParameters.load('stereo')
