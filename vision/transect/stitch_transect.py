import cv2
import numpy as np
import math

from vision.transect.transect_image import TransectImage
from vision.colors import *
from vision.transect.line import *

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

    def stitch(self, id):
        """
        
        """

        image = self.images[id].image

        # Finding the blue pole
        blue_mask, red_mask = self.color_masks(image)

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,50))
        vertical_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

        coords1_b, coords2_b = self.line_coords(vertical_mask)
        blue_lines = Line.new_lines(coords1_b, coords2_b)

        blue_extended = []
        for line in blue_lines:
            blue_extended.append(line.extended_line(image))

        blue_clusters = self.line_clusters(blue_extended, tol=1)
        print(len(blue_clusters))

        for line in blue_clusters:
            final_line = line.extended_line(image)

            # start = tuple(int(num) for num in final_line.start)
            # end = tuple(int(num) for num in final_line.end)

            cv2.line(image, final_line.start, final_line.end, (255, 0, 0), 10)

        blue_line = line

        # Finding the red lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
        horizontal_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        coords1_r, coords2_r = self.line_coords(horizontal_mask)

        red_lines = Line.new_lines(coords1_r, coords2_r)

        red_extended = []
        for line in red_lines:
            red_extended.append(line.extended_line(image))

        red_clusters = self.line_clusters(red_extended, tol=.5)
        
        count = 0

        for line in red_clusters:
            extended = line.extended_line(image)

            # Skip if line isn't close to horizontal
            if not math.isclose(abs(extended.angle), 0, abs_tol=.15):
                continue

            # Skip if line isn't orthogonal with the blue line 
            if not line.is_orthogonal(blue_line, tol=.09):
                continue

            count += 1
            cv2.line(image, extended.start, extended.end, (0, 0, 255), 10)

        print(count)
        self.all_images.append(image)
