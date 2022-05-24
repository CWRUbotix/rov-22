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

    def blue_mask(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Resizing to make kmeans color clustering run faster
        hsv_resized = imutils.resize(hsv_image, 100)
        colors_found = get_colors(hsv_resized, 10)

        # Make the blue mask
        hues = [i[0] for i in colors_found]

        BLUE_HSV_VAL = 120
        blue = colors_found[self.color_index(hues, BLUE_HSV_VAL)]

        lower_blue = np.array([blue[0]-20, 0, 0])
        upper_blue = np.array([blue[0]+20, 255, 255])

        blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

        return blue_mask

    def color_index(self, hues, color_hue):
        return hues.index(min(hues, key=lambda x:abs(x - color_hue)))

    def stitch(self, id):
        image = self.images[id].image
        blue_mask = self.blue_mask(image)

        # Find all the lines in the image
        lines = np.zeros_like(image)
        all_lines = cv2.HoughLinesP(blue_mask, 1, np.pi/180, 100, minLineLength=1000, maxLineGap=300)

        point1 = []
        point2 = []

        if all_lines is not None:
            for points in all_lines:
                x1, y1, x2, y2 = points[0]

                point1.append((x1, y1))
                point2.append((x2, y2))

                # cv2.line(lines, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Find the average line
        x1, y1 = [sum(x)/len(x) for x in zip(*point1)]
        x2, y2 = [sum(x)/len(x) for x in zip(*point2)]

        # Extend the line to the edges of the screen
        height, width, _ = image.shape

        slope = (y2 - y1)/(x2 - x1)
        y_intercept = y1 - slope * x1

        # y = mx + b -> solve for x
        x1 = (0 - y_intercept)/slope
        x2 = (height - y_intercept)/slope

        cv2.line(lines, (int(x1), 0), (int(x2), int(height)), (255, 0, 0), 10)

        self.all_images.append(lines)
