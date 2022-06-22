'''This script takes input from two cameras and takes captures simultaneously. Images are named 1.png, 2.png,...
Images from camera 1 are saved in a directory named "left"
Images from camera 2 are saved in a directory named "right"
Use the "c" key to take a capture.'''

import cv2

from os import path

from util import data_path

stereo_cam = True


vc1 = cv2.VideoCapture(1)

vc1.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
vc1.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

if not stereo_cam:
    vc2 = cv2.VideoCapture(2)

# Edit this to change the path where images are saved
image_path = path.join(data_path, 'stereo', 'dualcam1')
image_path_l = path.join(image_path, 'left')
image_path_r = path.join(image_path, 'right')

# Edit this to change starting number for file names
i = 1

while True:
    ret, cap1 = vc1.read()
    if ret:
        if stereo_cam:
            width = cap1.shape[1]
            half = int(width / 2)
            cap2 = cap1[:, half:width]
            cap1 = cap1[:, 0:half]
        else:
            ret, cap2 = vc2.read()

        cv2.imshow('Cam 1', cap1)
        cv2.imshow('Cam 2', cap2)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            file1 = path.join(image_path_l, str(i) + '.png')
            file2 = path.join(image_path_r, str(i) + '.png')

            cv2.imwrite(file1, cap1)
            cv2.imwrite(file2, cap2)

            i += 1