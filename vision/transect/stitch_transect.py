import cv2
import numpy as np
from vision.transect.transect_image import TransectImage

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)

    def set_image(self, key, image):
        self.images[key] = image

    def draw_lines(self, image, mask):
        """
        Draws detected lines on the given image

        :param image: image to draw the lines on
        :param mask: image to use to detect the lines
        """

        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=200)

        if lines is not None:
            for i in range(len(lines)):
                line = lines[i]

                x1, y1, x2, y2 = line.reshape(4)
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    def find_grid(self):
        image = self.images.get(1).image # make this more general later

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        lines = np.zeros_like(image)
        self.draw_lines(lines, edges)

        cv2.imshow("Image", lines)
        cv2.waitKey(0)

