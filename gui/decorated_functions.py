import cv2
from gui.decorator import Decorator

dropdown = Decorator()


@dropdown
def none(image):
    return image

@dropdown
def convert_to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


@dropdown
def test(image):
    print("test")
    return image
