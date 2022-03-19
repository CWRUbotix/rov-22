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
    Converts the given image to a bitmap that masks anything other than red
    :param image: image to convert
    :return: converted image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([155,25,0])
    upper = np.array([179,255,255])
    mask = cv2.inRange(hsv, lower, upper)

    masked = cv2.cvtColor(cv2.bitwise_and(hsv, hsv, mask=mask), cv2.COLOR_HSV2BGR)
    # gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    gray = masked[:,:,2]
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    width, height = thresh.shape
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    high_score = 0
    best_contour = None

    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        if w < width and h < height and w * h > high_score:
            high_score = w * h
            best_contour = contour
    
    if high_score > 0:
        x,y,w,h = cv2.boundingRect(best_contour)
        cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

    return image