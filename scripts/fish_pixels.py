"""Goes through the fish images for manually marking the ends of the fish"""

import cv2
import os
from os import path
from util import data_path    

def record_mouse_position(event, x, y, flag, params):
    """Records mouse position on click""" 

    if event == cv2.EVENT_LBUTTONDOWN:
 
        print(f"{x}, {y}")

def browse_images(image_path):
    """Browse images with the 'a' and 'd' keys"""

    images_list = [image_name for image_name in os.listdir(image_path)]
    index = 0

    window = "image"

    cv2.namedWindow(window)
        
    while True:
        image = cv2.imread(image_path +"/"+ images_list[index])
        image = cv2.putText(image, images_list[index], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window, image)
        cv2.setWindowProperty(window, cv2.WND_PROP_TOPMOST, 1)
        cv2.setMouseCallback(window, record_mouse_position)

        k = cv2.waitKey(0) & 0xFF

        # 'a' key to go back    
        if k == 97 and index > 0:
            index -= 1

        # 'd' key to go forwards
        elif k == 100 and index < len(images_list) - 1: 
            index += 1

        # 'esc' to quit
        elif k == 27: 
            cv2.destroyAllWindows()
            break

image_path_left = path.join(data_path, 'stereo', '1undistort', 'left')
image_path_right = path.join(data_path, 'stereo', '1undistort', 'right')

browse_images(image_path_left)
browse_images(image_path_right)