import os
import math
import cv2
import numpy as np
from os import path

from util import data_path

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


proj_l = np.array([[1149.734375, 0.0, 717.5405502319336, 0.0], [0.0, 1149.734375, 518.3698806762695, 0.0], [0.0, 0.0, 1.0, 0.0]])
proj_r = np.array([[1149.734375, 0.0, 717.5405502319336, -4005.0020285217283], [0.0, 1149.734375, 518.3698806762695, 0.0], [0.0, 0.0, 1.0, 0.0]])

Left_Stereo_Map0 = []
Left_Stereo_Map1 = []
Right_Stereo_Map0 = []
Right_Stereo_Map1 = []

cv_file = cv2.FileStorage("improved_params2.xml", cv2.FILE_STORAGE_READ)
Left_Stereo_Map0 = cv_file.getNode("Left_Stereo_Map_x").mat()
Left_Stereo_Map1 = cv_file.getNode("Left_Stereo_Map_y").mat()
Right_Stereo_Map0 = cv_file.getNode("Right_Stereo_Map_x").mat()
Right_Stereo_Map1 = cv_file.getNode("Right_Stereo_Map_y").mat()
cv_file.release()


for i in range(len(images)):
    imgL = left_images[i]
    imgR = right_images[i]
    imgL_gray = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    imgR_gray = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    outputL = imgL.copy()
    outputR = imgR.copy()

    Left_nice= cv2.remap(imgL_gray,Left_Stereo_Map0,Left_Stereo_Map1, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    Right_nice= cv2.remap(imgR_gray,Right_Stereo_Map0,Right_Stereo_Map1, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

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

        points3d = cv2.triangulatePoints(proj_l, proj_r, cornersL, cornersR)

        points3d /= points3d[3,:]
        point1 = points3d[:,0]
        point2 = points3d[:,-1]
        distance = math.dist(points3d[:,0], points3d[:,-1])
        print(distance)

        

