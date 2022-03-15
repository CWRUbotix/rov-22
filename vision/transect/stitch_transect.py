import cv2
from vision.transect.transect_image import TransectImage

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([1, 2, 3, 4, 5, 6, 7, 8], TransectImage)

    def set_image(self, key, image):
        self.images[key] = image

    def transect_image(self):
        return self.images.get(1)