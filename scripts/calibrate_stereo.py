import os
from vision.stereo.params import StereoParameters
import cv2
import numpy as np
from os import path

from util import data_path

directory = path.join(data_path, 'stereo-calibration', 'pool')

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

for i in range(len(images)):
	imgL = left_images[i]
	imgR = right_images[i]
	imgL_gray = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
	imgR_gray = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

	outputL = imgL.copy()
	outputR = imgR.copy()

	#retR, cornersR =  cv2.findChessboardCorners(outputR,(10,7),None, flags=cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)
	#retL, cornersL = cv2.findChessboardCorners(outputL,(10,7),None, flags=cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)

	retR, cornersR =  cv2.findChessboardCornersSB(outputR,(10,7),None, flags=cv2.CALIB_CB_EXHAUSTIVE+cv2.CALIB_CB_NORMALIZE_IMAGE)
	retL, cornersL = cv2.findChessboardCornersSB(outputL,(10,7),None, flags=cv2.CALIB_CB_EXHAUSTIVE+cv2.CALIB_CB_NORMALIZE_IMAGE)


	if retR and retL:
		obj_pts.append(objp)
		#cv2.cornerSubPix(imgR_gray,cornersR,(11,11),(-1,-1),criteria)
		#cv2.cornerSubPix(imgL_gray,cornersL,(11,11),(-1,-1),criteria)
		cv2.drawChessboardCorners(outputR,(10,7),cornersR,retR)
		cv2.drawChessboardCorners(outputL,(10,7),cornersL,retL)
		cv2.imshow('cornersR',outputR)
		cv2.imshow('cornersL',outputL)
		cv2.waitKey(0)

		img_ptsL.append(cornersL)
		img_ptsR.append(cornersR)

print('LENGTH: ' + str(len(img_ptsL)))

# Calibrating left camera
retL, mtxL, distL, rvecsL, tvecsL = cv2.calibrateCamera(obj_pts,img_ptsL,imgL_gray.shape[::-1],None,None)
hL,wL= imgL_gray.shape[:2]
new_mtxL, roiL= cv2.getOptimalNewCameraMatrix(mtxL,distL,(wL,hL),1,(wL,hL))

# Calibrating right camera
retR, mtxR, distR, rvecsR, tvecsR = cv2.calibrateCamera(obj_pts,img_ptsR,imgR_gray.shape[::-1],None,None)
hR,wR= imgR_gray.shape[:2]
new_mtxR, roiR= cv2.getOptimalNewCameraMatrix(mtxR,distR,(wR,hR),1,(wR,hR))

print(str(new_mtxL.tolist()))
print(str(new_mtxR.tolist()))

flags = 0
flags |= cv2.CALIB_FIX_INTRINSIC
# Here we fix the intrinsic camara matrixes so that only Rot, Trns, Emat and Fmat are calculated.
# Hence intrinsic parameters are the same 

criteria_stereo= (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# This step is performed to transformation between the two cameras and calculate Essential and Fundamenatl matrix
retS, new_mtxL, distL, new_mtxR, distR, Rot, Trns, Emat, Fmat = cv2.stereoCalibrate(obj_pts, img_ptsL, img_ptsR, new_mtxL, distL, new_mtxR, distR, imgL_gray.shape[::-1], criteria=criteria_stereo, flags=flags)

rectify_scale= 1
rect_l, rect_r, proj_mat_l, proj_mat_r, Q, roiL, roiR= cv2.stereoRectify(new_mtxL, distL, new_mtxR, distR, imgL_gray.shape[::-1], Rot, Trns, rectify_scale,(0,0))

print('Projection Matrices')
print(str(proj_mat_l.tolist()))
print(str(proj_mat_r.tolist()))

points = cv2.triangulatePoints(proj_mat_l, proj_mat_r, img_ptsL[0], img_ptsR[0])
#print(points)


Left_Stereo_Map= cv2.initUndistortRectifyMap(new_mtxL, distL, rect_l, proj_mat_l,
                                             imgL_gray.shape[::-1], cv2.CV_16SC2)
Right_Stereo_Map= cv2.initUndistortRectifyMap(new_mtxR, distR, rect_r, proj_mat_r,
                                              imgR_gray.shape[::-1], cv2.CV_16SC2)

parameters = StereoParameters(proj_mat_l, proj_mat_r, Left_Stereo_Map, Right_Stereo_Map)
parameters.save('stereo-pool')

print("Saving paraeters ......")
cv_file = cv2.FileStorage("improved_params2.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("Left_Stereo_Map_x",Left_Stereo_Map[0])
cv_file.write("Left_Stereo_Map_y",Left_Stereo_Map[1])
cv_file.write("Right_Stereo_Map_x",Right_Stereo_Map[0])
cv_file.write("Right_Stereo_Map_y",Right_Stereo_Map[1])
cv_file.release()


'''
cv2.imshow("Left image before rectification", imgL)
cv2.imshow("Right image before rectification", imgR)

Left_nice= cv2.remap(imgL,Left_Stereo_Map[0],Left_Stereo_Map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
Right_nice= cv2.remap(imgR,Right_Stereo_Map[0],Right_Stereo_Map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

cv2.imshow("Left image after rectification", Left_nice)
cv2.imshow("Right image after rectification", Right_nice)
cv2.waitKey(0)

out = Right_nice.copy()
out[:,:,0] = Right_nice[:,:,0]
out[:,:,1] = Right_nice[:,:,1]
out[:,:,2] = Left_nice[:,:,2]

cv2.imshow("Output image", out)
cv2.waitKey(0)
'''