"""Goes through the fish images for manually marking the ends of the fish"""

import cv2
from os import path, listdir
from util import data_path              

def view_images(image_path):

    for file in listdir(image_path):
        image = cv2.imread(image_path +"/"+ file)

        cv2.imshow("image", image)
        cv2.waitKey(0)

image_path_left = path.join(data_path, 'stereo', '1undistort', 'left')
image_path_right = path.join(data_path, 'stereo', '1undistort', 'right')

view_images(image_path_left)
view_images(image_path_right)




