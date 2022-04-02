import os
import math
from vision.stereo.params import StereoParameters
import cv2
import numpy as np
from os import path

from util import data_path

ACTUAL_LENGTH = 18.3

directory = path.join(data_path, 'stereo-calibration')

images = []
left_images = []
right_images = []

for filename in os.listdir(directory):
    image = cv2.imread(path.join(directory, filename))
    images.append(image)

    width = image.shape[1]
    half = int(width / 2)
    
    left_images.append(image[:,0:half])
    right_images.append(image[:,half:width])



# Termination criteria for refining the detected corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


objp = np.zeros((10*7,3), np.float32)
objp[:,:2] = np.mgrid[0:10,0:7].T.reshape(-1,2)

img_ptsL = []
img_ptsR = []
obj_pts = []


params = StereoParameters.load('stereo')
distances = []

for i in range(len(images)):
    imgL = left_images[i]
    imgR = right_images[i]
    imgL_gray = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    imgR_gray = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    outputL = imgL.copy()
    outputR = imgR.copy()

    Left_nice= cv2.remap(imgL_gray,params.left_rectify_map[0],params.left_rectify_map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    Right_nice= cv2.remap(imgR_gray,params.right_rectify_map[0],params.right_rectify_map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

    retR, cornersR =  cv2.findChessboardCorners(Right_nice,(10,7),None)
    retL, cornersL = cv2.findChessboardCorners(Left_nice,(10,7),None)

    if retR and retL:
        obj_pts.append(objp)

        

        cv2.cornerSubPix(Right_nice,cornersR,(11,11),(-1,-1),criteria)
        cv2.cornerSubPix(Left_nice,cornersL,(11,11),(-1,-1),criteria)
        cv2.drawChessboardCorners(Right_nice,(10,7),cornersR,retR)
        cv2.drawChessboardCorners(Left_nice,(10,7),cornersL,retL)
        #cv2.imshow('cornersR',Right_nice)
        #cv2.imshow('cornersL',Left_nice)
        #cv2.waitKey(0)

        points3d = cv2.triangulatePoints(params.proj_l, params.proj_r, cornersL, cornersR)

        points3d /= points3d[3,:]
        point1 = points3d[:,0]
        point2 = points3d[:,-1]
        distance = math.dist(points3d[:,0], points3d[:,-1])
        print(distance)
        distances.append(distance)


avg = sum(distances) / len(distances)

print(ACTUAL_LENGTH / avg)
