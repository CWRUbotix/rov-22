import cv2
import os
import unittest
from util import data_path

from vision.transect.transect_image import TransectImage
from vision.transect.stitch_transect import *
from vision.transect.stitch_auto import *
from vision.transect.stitch_manual import *
from vision.colors import *

def set_test_images():
    # Path to folder with test images
    folder_A = os.path.join(data_path, "transect", "stitching", "A")

    # Set image for each square in the stitcher
    for i in range(1, 9):

        test_set = 1 # Change this number to change the testing set

        subfolder_path = os.path.join(folder_A, str(i))
        image_name = os.listdir(subfolder_path)[test_set]
        complete_path = os.path.join(subfolder_path, image_name)

        image = TransectImage(i, cv2.imread(complete_path))

        stitcher.set_image(i, image)      

def set_pool_images():
    folder_path = os.path.join(data_path, "transect", "stitching", "p00l")

    files = [img_name for img_name in os.listdir(folder_path)]
    files.sort()

    for i in range(0, 8):
        image_path = os.path.join(folder_path, files[i])

        image = TransectImage(i+1, cv2.imread(image_path))
        stitcher.set_image(i+1, image)


class TestStitchTransect(unittest.TestCase):
    def stitched(self):
        set_test_images()

        for key in stitcher.images:
            set_lines(key)
            print(f"Finished with image {key}/8")

        stitched()

    def browse_images(self):
        """Browse through images with the 'a' and 'd' keys"""

        set_test_images()

        for key in stitcher.images:
            set_lines(key, debug=True)
            print(f"Finished with image {key}/8")

        # stitch()

        images_list = []

        for key in stitcher.images:
            images_list.append(stitcher.images[key].image)

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

    def stitch_manually(self):
        set_pool_images()
        stitch_manually()

if __name__ == "__main__":
    """
    To run a specific test:
    python3 vision/transect/stitch_transect_test.py TestStitchTransect.browse_images
    """

    unittest.main()