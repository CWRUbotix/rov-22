'''Script for generating fisheye calibration parameters. Source: https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0
Use the 10x7 checkerboard here: https://markhedleyjones.com/projects/calibration-checkerboard-collection
Point the camera at the checkerboard. Once it detects the checkerboard, the program will pause.
Move the camera to a new location. Press any key to unpause. It will then continue to look for a checkerboard.
Repeat this until program quits. Parameters will be printed to terminal.
'''
import cv2
import numpy as np

CHECKERBOARD = (10,7)
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

_img_shape = None
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

cam = cv2.VideoCapture(1)
#cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
while True:
    ret, img = cam.read()
    if img is None:
        continue
    if _img_shape == None and img is not None:
        print(img.shape)
        _img_shape = img.shape[:2]
    else:
        pass
        #assert _img_shape == img.shape[:2], "All images must share the same size." 
    
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
    # Find the chess board corners
    #corners, score = checkerboard.detect_checkerboard(img, CHECKERBOARD)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
        imgpoints.append(corners)
        cv2.imshow("Corners", img)
        cv2.waitKey(0)
        if len(objpoints) > 10:
            break
        

N_OK = len(objpoints)
print("NOK" + str(N_OK))
K = np.zeros((3, 3))
D = np.zeros((4, 1))
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
rms, _, _, _, _ = \
    cv2.fisheye.calibrate(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("Found " + str(N_OK) + " valid images for calibration")
print("DIM=" + str(_img_shape[::-1]))
print("K=np.array(" + str(K.tolist()) + ")")
print("D=np.array(" + str(D.tolist()) + ")")