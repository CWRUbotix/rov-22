'''Reads all the images in a directory, undistorts them, and saves them to a new directory'''

import cv2
import numpy as np
from os import path, listdir

from util import data_path, undistort

# Edit these directories
source_dir = path.join(data_path, 'stereo', '1', 'right')
dest_dir = path.join(data_path, 'stereo', '1undistort', 'right')

# Paste calibration parameters here
DIM=(640, 480)
K=np.array([[253.5047592756691, 0.0, 337.0384349728359], [0.0, 253.76547695471558, 235.03841855879503], [0.0, 0.0, 1.0]])
D=np.array([[-0.04113118666673021], [0.04015359029384363], [-0.05408029839243729], [0.0193079732018332]])

for filename in listdir(source_dir):
    file = path.join(source_dir, filename)
    dest_file = path.join(dest_dir, filename)

    image = cv2.imread(file)
    undistored = undistort(image, DIM, K, D)

    cv2.imwrite(dest_file, undistored)