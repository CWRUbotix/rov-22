"""Goes through the fish images for manually marking the ends of the fish"""

import cv2
import os
from os import path, listdir
from util import data_path              

def browse_images(image_path):
    """
    Browse images with the 'a' and 'd' keys
    """

    images_list = [image_name for image_name in os.listdir(image_path)]
    index = 0
        
    while True:
        image = cv2.imread(image_path +"/"+ images_list[index])
        cv2.imshow("image", image)

        k = cv2.waitKey(0) & 0xFF

        if k == 97 and index > 0:
            index -= 1

        elif k == 100 and index < len(images_list) - 1:
            index += 1

        elif k == 27:
            cv2.destroyAllWindows()
            break

image_path_left = path.join(data_path, 'stereo', '1undistort', 'left')
image_path_right = path.join(data_path, 'stereo', '1undistort', 'right')

browse_images(image_path_left)
browse_images(image_path_right)