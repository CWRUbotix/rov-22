import cv2
from gui.decorator import Decorator
import numpy as np

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
def convert_to_gray(image):
    """
    Converts the given image to a bitmap that masks anything other than red
    :param image: image to convert
    :return: converted image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([155,25,0])
    upper = np.array([179,255,255])
    mask = cv2.inRange(hsv, lower, upper)

    result = cv2.cvtColor(cv2.bitwise_and(hsv, hsv, mask=mask), cv2.COLOR_HSV2BGR)

    return result