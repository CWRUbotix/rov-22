import numpy as np
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
        """
        Given a startpoint and an endpoint in the form (x, y), returns a new Line
        
        @param start: startpoint of the line
        @param end: endpoint of the line
        @return: new Line
        """

        x1, y1 = start
        x2, y2 = end

        m = (y2 - y1)/(x2 -x1) if x2 - x1 != 0 else 0
        b = y1 - m * x1

        dx = x2 - x1
        dy = y2 - y1 
        angle = math.atan2(dy, dx)

        return cls((x1, y1), (x2, y2), m, b, angle)

    @classmethod
    def new_lines(cls, coords1, coords2):
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

    @classmethod
    def draw_lines(cls, image, lines, color=(0, 255,0), thickness=10):
        """
        Draws the Lines on an image
        
        @param image: image to draw the lines on
        @param lines: list of Lines to draw
        @param color: color of the lines
        @param thickness: thickness of the lines
        @return: image with lines drawn on
        """

        for line in lines:
            cv2.line(image, line.start, line.end, color, thickness)

        return image

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
        Returns the distance between the center of this line and the given line.

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
        """
        Returns a string representation of this Line

        @return: string with Line info
        """

        x1, y1 = self.start
        x2, y2 = self.end

        return f"({x1}, {y1}), ({x2}, {y2})"