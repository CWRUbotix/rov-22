import cv2
from gui.debug_filter import DebugFilter

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
