import cv2
import numpy as np
import imutils
from vision.transect.transect_image import TransectImage
from vision.colors import *

class Rectangle():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)

    def set_image(self, key, image):
        self.images[key] = image

    def find_rectangle(self):
        image = self.images.get(1).image # make this more general later

        # Find all the lines in the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        lines = np.zeros_like(image)
        all_lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=100)
        
        if all_lines is not None:
            for points in all_lines:
                x1, y1, x2, y2 = points[0]
                cv2.line(lines, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Make the lines thicker
        ksize2 = 10
        kernel = np.ones((ksize2, ksize2))
        lines = cv2.dilate(lines, kernel, iterations=4)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        # Find the rectangles in the frame
        rectangles = []

        contours, _ = cv2.findContours(lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt_frame = image.copy()

        height, width, _ = image.shape
        image_area = height * width

        for cnt in contours:
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, .01 * cv2.arcLength(cnt, True), True)

            # Filter contours by size
            if image_area * .04 < area:
                
                # Add contour to rectangles list if it has four sidess
                if len(approx) == 4:
                    cv2.drawContours(cnt_frame, [approx], 0, (255, 0, 0), 5)

                    x, y, w, h = cv2.boundingRect(approx)
                    rectangles.append(Rectangle(x, y, w, h))

        for r in rectangles:
            cv2.rectangle(image, (r.x, r.y), (r.x + r.w, r.y + r.h), (0, 255, 0), 5)

        cv2.imshow("Image", edges)
        cv2.waitKey(0)

    def colors(self, id):
        image = self.images.get(id).image
        image = imutils.resize(image, 100)
        
        get_colors(image, 10)

