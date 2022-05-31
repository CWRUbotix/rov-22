import cv2
from gui.debug_filter import DebugFilter
import numpy as np
from PIL import Image
from tasks.button_docking import get_button_contour

filter_dropdown = DebugFilter()

@filter_dropdown(name="None")
def none(image):
    """
    Returns the given image
    :param image: image to return
    :return: original image
    """
    return image


@filter_dropdown(name="Gray")
def convert_to_gray(image):
    """
    Converts the given image to grayscale
    :param image: image to convert
    :return: image converted to grayscale
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

@filter_dropdown(name="Mask for Red")
def mask_for_red(image):
    """
    Draws a green rectangle around the red button
    :param image: image to convert
    :return: converted image
    """
    best_contour, high_score = get_button_contour(image)
    
    # Calculate button position info if we found a good countour
    if high_score > 0:
        x,y,w,h = cv2.boundingRect(best_contour)
        cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

    return image