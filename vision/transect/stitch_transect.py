from math import atan2
from types import ClassMethodDescriptorType
import cv2
from cv2 import waitKey
import numpy as np
import imutils
import math
from vision.transect.transect_image import TransectImage
from vision.colors import *

class Line():
    def __init__(self, start, end, m, b):
        self.start = start
        self.end = end
        self.m = m
        self.b = b

    @classmethod
    def of(cls, start, end):
        x1, y1 = start
        x2, y2 = end
        
        m = (y2 - y1)/(x2 -x1) if x2 - x1 != 0 else 0
        b = y1 - m * x1

        return cls(start, end, m, b)

    def is_close(self, other, tol):
        """
        Returns if two lines are close

        @param other: line to compare with
        @param tol: tolerance for determining closeness
        @return: true if close, otherwise false
        """

        x1, y1 = self.start
        x2, y2 = self.end

        x3, y3 = other.start
        x4, y4 = other.end

        return all([math.isclose(x1, x3, rel_tol=tol),
                        math.isclose(y1, y3, rel_tol=tol), 
                        math.isclose(x2, x4, rel_tol=tol), 
                        math.isclose(y2, y4, rel_tol=tol)])

    def average_line(self, other):
        """
        Averages the current line with the given line and returns the new line

        @param other: line to average with
        @return: new average line
        """

        x1, y1 = self.start
        x2, y2 = self.end

        x3, y3 = other.start
        x4, y4 = other.end

        x1_avg = (x1 + x3)/2
        y1_avg = (y1 + y3)/2

        x2_avg = (x2 + x4)/2
        y2_avg = (y2 + y4)/2

        new_line = Line.of((x1_avg, y1_avg), (x2_avg, y2_avg))

        return new_line

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
        """
        Given an image, returns the blue and red color masks

        @param image: input image
        @return blue_mask, red_mask: the corresponding color masks
        """

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

    def line_coords(self, mask):
        """
        Given a color mask, performs line detection and returns two lists of coordinates that represent the endpoints of lines

        @param mask: color mask to use for line detection
        @return coords1, coords2
        """

        all_lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=1000, maxLineGap=300)

        coords1 = []
        coords2 = []

        if all_lines is not None:
            for points in all_lines:
                x1, y1, x2, y2 = points[0]

                coords1.append((x1, y1))
                coords2.append((x2, y2))

        return coords1, coords2

    def updated_cluster(self, line, clusters, tol):
        """
        Adds the given line to the appropriate cluster and returns the new cluster

        @param line: line to add
        @param clusters: the current cluster list
        @param tol: tolerance for determining closeness to other clusters
        @returns: updated cluster
        """

        # If clusters is empty add the computed avg line
        if not clusters:
            clusters.append(line)
            return clusters

        # Check if computed line fits in an existing cluster
        for i in range(len(clusters)):
            curr_line = clusters[i]

            if line.is_close(curr_line, tol):
            # if self.lines_are_close(curr_line, line, tol):
                clusters[i] = line.average_line(curr_line)  
                return clusters              

        clusters.append(line)

        return clusters

    def line_clusters(self, coords1, coords2, tol):
        """
        Finds clusters of lines that are close to each other and turns them into a single line

        @param coords1: list of line start points
        @param coords2: list of line end points
        @return: list of start points and list of end points of the average line from each cluster
        """

        if len(coords1) != len(coords2):
            raise Exception(f"Lists should be the same length: {len(coords1)} != {len(coords2)}")

        clusters = []

        for i in range(len(coords1)-1):
            line1 = Line.of(coords1[i], coords2[i])
            line2 = Line.of(coords1[i+1], coords2[i+1])

            clusters = self.updated_cluster(line1, clusters, tol)
            clusters = self.updated_cluster(line2, clusters, tol)

        return clusters

    def stitch(self, id):
        image = self.images[id].image

        # Finding the blue pole
        blue_mask, red_mask = self.color_masks(image)

        height, width, _ = image.shape

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,50))
        vertical_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

        coords1_b, coords2_b = self.line_coords(vertical_mask)
        blue_clusters = self.line_clusters(coords1_b, coords2_b, 1)

        print(len(blue_clusters))

        for line in blue_clusters:
            x1, y1 = line.start
            x2, y2 = line.end

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
            angle_b = atan2(dy,dx)

            cv2.line(image, (int(x1), 0), (int(x2), height), (255, 0, 0), 10)

        x1_b = x1
        x2_b = x2

        # Finding the red lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
        horizontal_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        coords1_r, coords2_r = self.line_coords(horizontal_mask)
        red_clusters = self.line_clusters(coords1_r, coords2_r, tol=.5)

        print(len(red_clusters))

        # for i in range(len(coords1_r)):
        for line in red_clusters:
            # x1, y1 = coords1_r[i]
            # x2, y2 = coords2_r[i]

            x1, y1 = line.start
            x2, y2 = line.end

            dx = x2 - x1
            dy = y2 - y1 
            angle = atan2(dy,dx)

            # Skip if line isn't close to horizontal
            if not math.isclose(abs(angle), 0, abs_tol=.15):
                continue

            # Extend the line to the edges of the screen
            delta_x = x2 - x1

            if delta_x != 0:
                slope = (y2 - y1)/delta_x
                y_intercept = y1 - slope * x1
        
                # y = mx + b -> solve for y
                y1 = slope * x1 + y_intercept
                y2 = slope * x2 + y_intercept

            # Skip if line isn't orthogonal with the blue line 
            vec_b = np.array([x1_b - x2_b, 0 - height])
            vec_r = np.array([0 - width, y1 - y2])

            unit_vec_b = vec_b / np.linalg.norm(vec_b)
            unit_vec_r = vec_r / np.linalg.norm(vec_r)

            dot_prod = abs(np.dot(unit_vec_b, unit_vec_r))

            if not math.isclose(dot_prod, 0, abs_tol=.1):
                continue

            cv2.line(image, (0, int(y1)), (width, int(y2)), (0, 0, 255), 10)

        self.all_images.append(image)
