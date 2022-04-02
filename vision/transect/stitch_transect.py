import cv2
import numpy as np
import imutils
from vision.transect.transect_image import TransectImage
from vision.colors import *

class Rectangle():
    def __init__(self, x, y, w, h, cnt):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cnt = cnt

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)
        self.rect_images = []

    def set_image(self, key, image):
        self.images[key] = image

    def colors(self, id):
        image = self.images.get(id).image

        resized_image = imutils.resize(image, 100)
        
        hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

        colors_found = get_colors(hsv_image, 10)

        hues = [i[0] for i in colors_found]

        blue = colors_found[self.color_index(hues, 120)]
        yellow = colors_found[self.color_index(hues, 30)]

        lower_blue, upper_blue = self.bounds(blue)
        lower_yellow, upper_yellow = self.bounds(yellow)

        blue_mask = cv2.inRange(image, lower_blue, upper_blue)
        yellow_mask = cv2.inRange(image, lower_yellow, upper_yellow)

        mask = blue_mask + yellow_mask
        mask = cv2.bitwise_not(mask)
        
        return mask

    def color_index(self, hues, color_hue):
        return hues.index(min(hues, key=lambda x:abs(x - color_hue)))

    def bounds(self, color):
        lower_bound = np.array([color[0]-50, color[1]-50, color[2]-100])
        upper_bound = np.array([color[0]+50, color[1]+50, color[2]+100])

        return lower_bound, upper_bound

    def find_rectangle(self, id):
        image = self.images.get(id).image

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges1 = cv2.Canny(gray, 50, 150, apertureSize=3)

        mask = self.colors(id)
        edges2 = cv2.Canny(mask, 50, 150, apertureSize=3)

        height, width = edges1.shape
        edges2 = imutils.resize(edges2, width, height)

        edges = edges1 + edges2

        # Find all the lines in the image
        lines = np.zeros_like(image)
        all_lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=400, maxLineGap=100)
        
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

        height, width = image.shape[:2]
        image_area = height * width

        contours, _ = cv2.findContours(lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)

            # Filter out small rectangles
            if area < image_area * .1:
                continue

            # Filter out irregular contours
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            solidity = float(area)/hull_area

            if solidity < .9:
                continue

            # Filter out rectangles with irregular width to height ratio
            (x, y, w, h) = cv2.boundingRect(c)
            dim_error = (abs(w - h)/w)  # Error between width and height

            if dim_error > .8:
                continue

            # Add rect to rectangles list
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            rectangles.append(Rectangle(x, y, w, h, [box]))

        rect_image = image.copy()
        self.rect_images.append(rect_image)

        # Draw rectangles on the image
        for r in rectangles:            
            cv2.rectangle(rect_image, (r.x, r.y), (r.x + r.w, r.y + r.h), (0, 255, 0), 5)

            # cv2.drawContours(image, r.cnt, 0, (0, 255, 0), 10)