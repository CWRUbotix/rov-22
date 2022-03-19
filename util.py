import argparse
import json
from os import path

import cv2
import numpy as np

from logger import root_logger

logger = root_logger.getChild(__name__)

vision_path = path.dirname(__file__)

#If your repository paths do not match the following defaults, copy the "config/resource-paths.json.default" file to "config/resource-paths-paths.json" and edit.
try:
    with open('config/resource-paths.json', 'r') as paths_file:
        paths = json.load(paths_file)
        data_path = path.abspath(paths['data_path'])
        ardupilot_path = path.abspath(paths['ardupilot_path'])
        gazebo_path = path.abspath(paths['gazebo_path'])
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    logger.debug('config/resource-paths.json not found or is invalid, using default resource paths')
    parent_dir = path.split(vision_path)[0]
    data_path = path.join(parent_dir, 'data')
    ardupilot_path = path.join(parent_dir, 'ardupilot')
    gazebo_path = path.join(parent_dir, 'gazebo_rov')
ardusub_path = path.join(ardupilot_path, 'ArduSub')


def config_parser(config_dir: str):
    '''Returns a function to parse config files. config_dir is the directory within the 'config' directory where the parser will look for files'''
    def parse(arg: str):
        file = path.join(path.dirname(__file__), 'config', config_dir, arg)
        if not path.isfile(file):
            raise argparse.ArgumentError(None, 'File does not exist in config/' + config_dir + ' directory')
        return open(file, 'r')

    return parse


def undistort(img, DIM, K, D, balance=0.0, dim2=None, dim3=None) -> np.ndarray:
    '''
    Undistorts a fisheye image using the `DIM`, `K`, `D` parameters.

    `balance` is a number between 0 and 1 indicating how much of the edges to crop out.

    Source: https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-part-2-13990f1b157f
    '''
    dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img