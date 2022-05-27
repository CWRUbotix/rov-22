from math import atan2
from pickletools import read_stringnl_noescape
from types import ClassMethodDescriptorType
import cv2
from cv2 import waitKey
import numpy as np
import imutils
import math
from vision.transect.transect_image import TransectImage
from vision.colors import *

class Line():
    def __init__(self, start, end, m, b, angle):
        self.start = start
        self.end = end
        self.m = m
        self.b = b
        self.angle = angle

    @classmethod
    def of(cls, start, end):
        x1, y1 = start
        x2, y2 = end

        m = (y2 - y1)/(x2 -x1) if x2 - x1 != 0 else 0
        b = y1 - m * x1

        dx = x2 - x1
        dy = y2 - y1 
        angle = atan2(dy, dx)

        return cls((x1, y1), (x2, y2), m, b, angle)

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

    def extended_line(self, image):
        """
        Creates an extended version of this line to the edge of the given image

        @param image: image the line belongs to
        @returns: a new line line extended to the edges of the given image
        """

        height, width, _ = image.shape

        x1, y1 = self.start
        x2, y2 = self.end

        angle = abs(self.angle)

        # Check if the line is horziontal or vertical
        if abs(angle - 1.5708) >= angle:
            # Horizontal

            if self.m != 0:
                # y = mx + b -> solve for y
                y1 = self.m * x1 + self.b
                y2 = self.m * x2 + self.b

            return Line.of((0, int(y1)), (width, int(y2)))
        
        else:
            # Vertical
            
            if self.m != 0:
                # y = mx + b -> solve for x
                x1 = (0 - self.b)/self.m
                x2 = (height - self.b)/self.m

            return Line.of((int(x1), 0), (int(x2), height))

    def distance(self, other):
        """
        Returns the distance between this line and the given line.

        @param other: line to compare to
        @return: distance
        """

        x1, y1 = self.start
        x2, y2 = self.end

        x3, y3 = other.start
        x4, y4 = other.end

        # Find the center of point of each line
        x = (x1 + x2)/2
        y = (y1 + y2)/2

        xo = (x3 + x4)/2
        yo = (y3 + y4)/2

        # Calculate the distance
        return math.sqrt((x - xo)**2 + (y - yo)**2)

    def is_orthogonal(self, other, tol=0):
        """
        Compares this line to the given line and returns whether they are orthogonal to each other

        @param other: line to compare to
        @param tol: tolerance for determining orthgonality
        @returns: true if the line is orthogonal, otherwise false
        """

        x1, y1 = self.start
        x2, y2 = self.end

        x3, y3 = other.start
        x4, y4 = other.end

        # Create vectors
        vec1 = np.array([x1 - x2, y1 - y2])
        vec2 = np.array([x3 - x4, y3 - y4])

        # Convert to unit vectors
        unit_vec1 = vec1 / np.linalg.norm(vec2)
        unit_vec2 = vec2 / np.linalg.norm(vec2)

        dot_prod = abs(np.dot(unit_vec1, unit_vec2))

        return math.isclose(dot_prod, 0, abs_tol=tol)

    def to_string(self):
        x1, y1 = self.start
        x2, y2 = self.end

        return f"({x1}, {y1}), ({x2, y2})"

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

        potential = []

        min = np.Inf
        min_index = 0

        # Check if computed line fits in an existing cluster
        for i in range(len(clusters)):
            curr_line = clusters[i]

            # if line.is_close(curr_line, tol) and line.distance(curr_line) < 500:
            if line.distance(curr_line) < 500:
                potential.append(i)

        if not potential:
            clusters.append(line)
            return clusters

        min = np.Inf
        min_index = 0

        for i in range(len(potential)):
            curr_line = clusters[i]

            if line.distance(curr_line) < min:
                min_index = potential[i]

        line_avg = line.average_line(clusters[min_index])
        clusters[min_index] = line_avg

        return clusters

    def line_clusters(self, lines, tol):
        """
        Finds clusters of lines that are close to each other and turns them into a single line

        @param coords1: list of line start points
        @param coords2: list of line end points
        @return: list of start points and list of end points of the average line from each cluster
        """

        clusters = []

        for line in lines:
            clusters = self.updated_cluster(line, clusters, tol)

        return clusters

    def new_lines(self, coords1, coords2):
        """
        Given a list of start coordinates and end coordinates, returns a list of Lines

        @param coords1: list of start coords
        @param coords2: list of end coords
        @return: list of Lines
        """

        if len(coords1) != len(coords2):
            raise Exception(f"Lists should be the same length: {len(coords1)} != {len(coords2)}")

        lines = []

        for i in range(len(coords1)):
            lines.append(Line.of(coords1[i], coords2[i]))

        return lines

    def stitch(self, id):

        image = self.images[id].image

        # Finding the blue pole
        blue_mask, red_mask = self.color_masks(image)

        height, width, _ = image.shape

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,50))
        vertical_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

        coords1_b, coords2_b = self.line_coords(vertical_mask)
        blue_lines = self.new_lines(coords1_b, coords2_b)

        blue_extended = []
        for line in blue_lines:
            blue_extended.append(line.extended_line(image))

        blue_clusters = self.line_clusters(blue_extended, tol=1)
        print(len(blue_clusters))

        for line in blue_clusters:
            final_line = line.extended_line(image)

            start = tuple(int(num) for num in final_line.start)
            end = tuple(int(num) for num in final_line.end)

            cv2.line(image, start, end, (255, 0, 0), 10)

        blue_line = line

        # Finding the red lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
        horizontal_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        coords1_r, coords2_r = self.line_coords(horizontal_mask)

        red_lines = self.new_lines(coords1_r, coords2_r)

        red_extended = []
        for line in red_lines:
            red_extended.append(line.extended_line(image))

        red_clusters = self.line_clusters(red_extended, tol=.5)
        print(len(red_clusters))

        for line in red_clusters:
            extended = line.extended_line(image)

            # Skip if line isn't close to horizontal
            if not math.isclose(abs(extended.angle), 0, abs_tol=.15):
                continue

            # Skip if line isn't orthogonal with the blue line 
            if not line.is_orthogonal(blue_line, tol=.09):
                continue

            cv2.line(image, extended.start, extended.end, (0, 0, 255), 10)

        self.all_images.append(image)
