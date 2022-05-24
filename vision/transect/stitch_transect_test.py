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

            test_set = 3 # Change this number to change the testing set

            subfolder_path = os.path.join(folder_A, str(i))
            image_name = os.listdir(subfolder_path)[test_set]
            complete_path = os.path.join(subfolder_path, image_name)

            image = TransectImage(i, cv2.imread(complete_path))

            self.stitcher.set_image(i, image)

    def find_rectangle(self):
        self.stitcher.find_rectangle(1)

    def colors(self):
        self.stitcher.colors(3)

    def browse_images(self):
        """
        Browse through images with the 'a' and 'd' keys
        """

        print("Starting k means color clustering...")

        for key in self.stitcher.images:
            self.stitcher.stitch(key)
            print(f"Finished with image {key}/8")

        images_list = self.stitcher.all_images

        index = 0

        window = "image"
        cv2.namedWindow(window)
        
        # Display the images
        while True:

            image = images_list[index]
            image_text = "Image: " + str(index+1)

            image = cv2.putText(image, image_text, (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 3, cv2.LINE_AA)

            cv2.imshow(window, image)

            k = cv2.waitKey(0) & 0xFF

            # 'a' key to go back    
            if k == 97 and index > 0:
                index -= 1

            # 'd' key to go forwards
            elif k == 100 and index < len(images_list) - 1: 
                index += 1

            # 'q' to quit
            elif k == 113: 
                cv2.destroyAllWindows()
                break

if __name__ == "__main__":
    """
    To run a specific test:
    python3 vision/transect/stitch_transect_test.py TestStitchTransect.browse_images
    """

    unittest.main()