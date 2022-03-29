import cv2
import os
import unittest
from util import data_path

from vision.transect.transect_image import TransectImage
from vision.transect.stitch_transect import StitchTransect
from vision.colors import *

class TestStitchTransect(unittest.TestCase):

    def setUp(self):
        self.stitcher = StitchTransect()

        # Path to folder with test images
        folder_A = os.path.join(data_path, "transect", "stitching", "A")

        # Set image for each square in the stticher
        for i in range(1, 9):

            subfolder_path = os.path.join(folder_A, str(i))
            image_name = os.listdir(subfolder_path)[0]
            complete_path = os.path.join(subfolder_path, image_name)

            image = TransectImage(i, cv2.imread(complete_path))

            self.stitcher.set_image(i, image)

    def test_find_rectangle(self):
        self.stitcher.find_rectangle()

    def test_colors(self):
        self.stitcher.colors(8)

if __name__ == "__main__":
    """
    To run a specific test:
    python3 vision/transect/stitch_transect_test.py TestStitchTransect.<name of test>
    """

    unittest.main()