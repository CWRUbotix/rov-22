import cv2
from cv2 import Stitcher
import numpy as np
import math
import imutils

from vision.transect.transect_image import TransectImage
from vision.colors import *
from vision.transect.line import *

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)

    def set_image(self, key, trans_img):
        # If the image is horizontal, flip it to be vertical
        # TEMPORARY FIX DELETE BEFORE COMPETITION
        height, width, _ = trans_img.image.shape

        if width > height:
            trans_img.image = cv2.rotate(trans_img.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.images[key] = trans_img

stitcher = StitchTransect()

class Rectangle():
    def __init__(self, x, y, w, h, cnt):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cnt = cnt

def color_masks(key):
    """
    Given an image, returns the blue and red color masks

    @param key: 
    @return blue_mask, red_mask: the corresponding color masks
    """

    image = stitcher.images[key].image
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
    red_mask = eroded_mask(red_mask) # Get rid of large red objects  

    # Make the yellow mask
    lower_yellow = np.array([22, 93, 0])
    upper_yellow = np.array([45, 255, 255])

    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    cv2.imshow("", yellow_mask)
    cv2.waitKey(0)

    return blue_mask, red_mask, yellow_mask

def line_coords( mask):
    """
    Given a color mask, performs line detection and returns two lists of coordinates that represent the endpoints of lines

    @param mask: color mask to use for line detection
    @return coords1, coords2
    """

    all_lines = cv2.HoughLinesP(mask, 1, np.pi/180, 500, minLineLength=1000, maxLineGap=300)

    coords1 = []
    coords2 = []

    if all_lines is not None:
        for points in all_lines:
            x1, y1, x2, y2 = points[0]

            coords1.append((x1, y1))
            coords2.append((x2, y2))

    return coords1, coords2

def updated_cluster(line, clusters, tol):
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

def line_clusters(lines, tol):
    """
    Finds clusters of lines that are close to each other and turns them into a single line

    @param coords1: list of line start points
    @param coords2: list of line end points
    @return: list of start points and list of end points of the average line from each cluster
    """

    clusters = []

    for line in lines:
        clusters = updated_cluster(line, clusters, tol)

    return clusters

def eroded_mask(mask):
    kernel = np.ones((30, 30), np.uint8)
    eroded = cv2.erode(mask, kernel) 

    kernel = np.ones((100, 100), np.uint8)
    dilated = cv2.dilate(eroded, kernel)

    new_mask = cv2.bitwise_and(mask, cv2.bitwise_not(dilated)) 

    return new_mask

def vertical_line(image, mask):
    """
    
    """

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,50))
    vertical_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    coords1_b, coords2_b = line_coords(vertical_mask)
    lines = Line.new_lines(coords1_b, coords2_b)

    extended = []
    for line in lines:
        extended.append(line.extended_line(image))

    clusters = line_clusters(extended, tol=1)
    print(len(clusters))

    for line in clusters:
        final_line = line.extended_line(image)

    return final_line

def horizontal_lines(image, mask, blue_line):
    """
    
    """

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
    horizontal_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

    coords1_r, coords2_r = line_coords(horizontal_mask)

    red_lines = Line.new_lines(coords1_r, coords2_r)

    red_extended = []
    for line in red_lines:
        red_extended.append(line.extended_line(image))

    red_lines = []

    for line in red_extended:
        # Skip if line isn't close to horizontal
        if not math.isclose(abs(line.angle), 0, abs_tol=.15):
            continue

        # Skip if line isn't orthogonal with the blue line 
        if not line.is_orthogonal(blue_line, tol=.09):
            continue

        red_lines.append(line)

    red_clusters = line_clusters(red_lines, tol=.5)

    final_lines = []

    count = 0
    for line in red_clusters:
        extended = line.extended_line(image)
        final_lines.append(extended)
        
        count += 1
    print(count)

    return final_lines

def set_lines(key, debug=False):
    """
    
    """

    image = stitcher.images[key].image

    blue_mask, red_mask, yellow_mask = color_masks(key)

    blue_line = vertical_line(image, blue_mask) # blue pole
    red_line_v = vertical_line(image, red_mask) # vertical red string

    horz_mask = red_mask

    # Use yellow mask for specific squares
    if key in [1, 2, 7, 8]:
        horz_mask = cv2.bitwise_or(red_mask, yellow_mask) 
    
    lines_h = horizontal_lines(image, horz_mask, blue_line)

    # Set lines for the current TransectImage
    trans_img = stitcher.images[key]

    trans_img.vertical_lines = [blue_line, red_line_v]
    trans_img.horizontal_lines = lines_h

    if debug:
        image = Line.draw_lines(image, blue_line, color=(0, 255, 0))
        image = Line.draw_lines(image, red_line_v, color=(0, 255, 0))
        image = Line.draw_lines(image, lines_h, color=(0, 255, 0))

    # x, y = Line.intersection(trans_img.blue_line, trans_img.red_lines_h[0])
    # image = cv2.circle(image, (x,y), radius=0, color=(0, 0, 0), thickness=-1)

def cropped_images(debug=False):
    """
    
    """

    cropped = []

    for key in stitcher.images:
        trans_img = stitcher.images[key]
        image = trans_img.image

        x1, y1 = Line.intersection(trans_img.vertical_lines[0], trans_img.horizontal_lines[0])
        x2, y2 = Line.intersection(trans_img.vertical_lines[0], trans_img.horizontal_lines[1])
        x3, y3 = Line.intersection(trans_img.vertical_lines[1], trans_img.horizontal_lines[0])
        x4, y4 = Line.intersection(trans_img.vertical_lines[1], trans_img.horizontal_lines[1])

        coords = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

        # Figure out which coordinate is for which corner
        coords.sort(key=lambda coord: coord[1])
        
        upper = [coords[0], coords[1]]
        lower = [coords[2], coords[3]]

        upper.sort(key=lambda coord: coord[0])
        lower.sort(key=lambda coord: coord[0])

        x1, y1 = upper[0] # top left
        x2, y2 = upper[1] # top right
        x3, y3 = lower[0] # bottom left
        x4, y4 = lower[1] # bottom right

        if debug:
            image = cv2.circle(image, (x1, y1), radius=0, color=(0, 255, 0), thickness=50)
            image = cv2.circle(image, (x2, y2), radius=0, color=(0, 255, 0), thickness=50)
            image = cv2.circle(image, (x3, y3), radius=0, color=(0, 255, 0), thickness=50)
            image = cv2.circle(image, (x4, y4), radius=0, color=(0, 255, 0), thickness=50)

        # Warp image 
        height, width, _ = image.shape

        src = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, x4]])
        dst = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        matrix = cv2.getPerspectiveTransform(src, dst)
        
        # Perspective transform original image
        warped = cv2.warpPerspective(image, matrix, (width, height))

        resized = imutils.resize(warped, width=400)        
        cropped.append(resized)

        if debug:
            cv2.imshow('warped', resized)
            cv2.waitKey(0)

    return cropped

def stitched():
    """
    
    """

    cropped = cropped_images()
    
    height, width, _ = cropped[0].shape

    final_height = height * 4
    final_width = width * 2

    final_image = np.zeros((final_height, final_width, 3), np.uint8) 
    print(final_image.shape)

    # Start from bottom left of final image
    id = 0
    y = final_height

    for i in range(4):
        x = 0
        for j in range(2):
            final_image[y-height:y, x:x+width] = cropped[id]

            x += width
            id += 1
        y -= height

    cv2.imshow("", final_image)
    cv2.waitKey(0)

def stitch_manually():
    """
    Stitch manually
    """



    pass
