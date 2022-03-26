import cv2
from gui.decorator import Decorator
import numpy as np
from PIL import Image

dropdown = Decorator()


@dropdown(name="None")
def none(image):
    """
    Returns the given image
    :param image: image to return
    :return: original image
    """
    return image


@dropdown(name="Gray")
def convert_to_gray(image):
    """
    Converts the given image to grayscale
    :param image: image to convert
    :return: image converted to grayscale
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

@dropdown(name="Mask for Red")
def mask_for_red(image):
    """
    Draws a green rectangle around the red button
    :param image: image to convert
    :return: converted image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Mask out non-red stuff
    lower = np.array([155,25,0])
    upper = np.array([179,255,255])
    mask = cv2.inRange(hsv, lower, upper)
    masked = cv2.cvtColor(cv2.bitwise_and(hsv, hsv, mask=mask), cv2.COLOR_HSV2BGR)

    # Get grayscale of red channel
    gray = masked[:,:,2]

    # Threshold it for a bitmap around redest stuff
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    height, width = thresh.shape  # yes, they're backwards, idk why

    # Find the largest contour
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    high_score = 0
    best_contour = None
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        if w < width and h < height and w * h > high_score:
            high_score = w * h
            best_contour = contour
    
    # Calculate button position info if we found a good countour
    if high_score > 0:
        x,y,w,h = cv2.boundingRect(best_contour)
        cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

    return image