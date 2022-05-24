from math import atan2
import cv2
from cv2 import waitKey
import numpy as np
import imutils
from vision.transect.transect_image import TransectImage
from vision.colors import *

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)
        self.all_images = []

    def set_image(self, key, trans_img):
        # If the image is horizontal, flip it to be vertical
        # TEMPORARY FIX DELETE BEFORE COMPETITION
        height, width, _ = trans_img.image.shape

        if width > height:
            trans_img.image = cv2.rotate(trans_img.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.images[key] = trans_img

    def color_masks(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Make the blue mask
        lower_blue = np.array([100, 0, 0])
        upper_blue = np.array([120, 255, 255])

        blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

        # Make the red mask
        lower_red = np.array([0,50,50])
        upper_red = np.array([10,255,255])
        red_mask1 = cv2.inRange(hsv_image, lower_red, upper_red)

        lower_red = np.array([170,50,50])
        upper_red = np.array([180,255,255])
        red_mask2 = cv2.inRange(hsv_image, lower_red, upper_red)

        red_mask = red_mask1 + red_mask2

        return blue_mask, red_mask

    def lines_image(self, mask):
        all_lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=1000, maxLineGap=300)

        coords1 = []
        coords2 = []

        if all_lines is not None:
            for points in all_lines:
                x1, y1, x2, y2 = points[0]

                coords1.append((x1, y1))
                coords2.append((x2, y2))

        return coords1, coords2

    def stitch(self, id):
        image = self.images[id].image
        blue_mask, red_mask = self.color_masks(image)

        height, width, _ = image.shape

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,50))
        vertical_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

        coords1_b, coords2_b = self.lines_image(vertical_mask)

        # Find the average line
        x1, y1 = [sum(x)/len(x) for x in zip(*coords1_b)]
        x2, y2 = [sum(x)/len(x) for x in zip(*coords2_b)]

        # Extend the line to the edges of the screen
        delta_x = x2 - x1

        if delta_x != 0:
            slope = (y2 - y1)/delta_x
            y_intercept = y1 - slope * x1
    
            # y = mx + b -> solve for x
            x1 = (0 - y_intercept)/slope
            x2 = (height - y_intercept)/slope

        dx = x2 - x1
        dy = height - 0 
        angle_b = abs(atan2(dy,dx))

        cv2.line(image, (int(x1), 0), (int(x2), height), (255, 0, 0), 10)

        # RED
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
        horizontal_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        coords1_r, coords2_r = self.lines_image(horizontal_mask)

        for i in range(len(coords1_r)):
            x1, y1 = coords1_r[i]
            x2, y2 = coords2_r[i]

            dx = x2 - x1
            dy = y2 - y1 
            angle = abs(atan2(dy,dx))

            # Skip if line isn't horizontal
            if abs(angle - .1)/.1 > 1:
                continue

            # Skip if line isn't a right angle with the blue line ...

            # Extend the line to the edges of the screen
            delta_x = x2 - x1

            if delta_x != 0:
                slope = (y2 - y1)/delta_x
                y_intercept = y1 - slope * x1
        
                # y = mx + b -> solve for y
                y1 = slope * x1 + y_intercept
                y2 = slope * x2 + y_intercept

            cv2.line(image, (0, int(y1)), (width, int(y2)), (0, 0, 255), 10)

        self.all_images.append(image)
