import cv2
from cv2 import waitKey
import numpy as np
import imutils
from vision.transect.transect_image import TransectImage
from vision.colors import *

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)
        self.rect_images = []

    def set_image(self, key, image):
        self.images[key] = image

    def get_matches(self, img1_gray, img2_gray):
        orb = cv2.ORB_create(nfeatures=1000)
        kp1, desc1 = orb.detectAndCompute(img1_gray, None)
        kp2, desc2 = orb.detectAndCompute(img2_gray, None)

        matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = matcher.knnMatch(desc1, desc2, k=2)

        good_matches = []
        for match_1, match_2 in matches:
            if match_1.distance < 0.6 * match_2.distance:
                good_matches.append(match_1)

        draw_params = dict(matchColor=(0,255,0),
                            singlePointColor=None,
                            flags=2)

        img3 = cv2.drawMatches(img1_gray,kp1, img2_gray,kp2, good_matches,None,**draw_params)
        # cv2.imshow("original_image_drawMatches.jpg", img3)
        # cv2.waitKey(0)

        good_kp1 = []
        good_kp2 = []

        for match in good_matches:
            good_kp1.append(kp1[match.queryIdx].pt) # keypoint in image A
            good_kp2.append(kp2[match.trainIdx].pt) # matching keypoint in image B

        return np.array(good_kp1), np.array(good_kp2)    

    def stitch_pair(self, img1, img2):
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        matches1, matches2 = self.get_matches(img1, img2)

        h_mat, mask = cv2.findHomography(matches1, matches2, cv2.RANSAC, ransacReprojThreshold=2.0)

        canvas = cv2.warpPerspective(img2, h_mat, (img1.shape[1] + img2.shape[1], img1.shape[0]))
        canvas[:, 0:img1.shape[1], :] = img1[:, :, :]

        cv2.imshow("final", canvas)
        cv2.waitKey(0)

    def stitch(self):
        self.stitch_pair(self.images[1].image, self.images[2].image)
