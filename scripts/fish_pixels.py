"""Goes through the fish images for manually marking the ends of the fish"""

from vision.stereo.stereo_util import left_half, right_half
from vision.stereo.pixels import PixelSelector
from vision.stereo.params import StereoParameters
import cv2
import os
from util import data_path    

num_clicks = 0

def record_mouse_position(event, x, y, flags, param):
    """
    Records mouse position on click to the specified file. Saved in the format: label/img_name x1 y1 x2 y2.
    """ 

    global num_clicks

    file = param[0]
    label = param[1]
    image_name = label+"/"+param[2]

    # Get mouse coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        coords = f" {x} {y}"

        # Format coordinates on the text file
        if num_clicks % 2 == 0:
            if num_clicks != 0:
                file.write("\n")
                print()

            file.write(image_name)
            print(image_name, end="")

        file.write(coords)
        print(coords, end="")                

        num_clicks += 1

def browse_images(file_path, images_path, stereo_params: StereoParameters, label=""):
    """
    Browse through images with the 'a' and 'd' keys

    :param file_path: path to text file to write the coordinates to
    :param images_path: path to the images to look through
    :param label: optional text printed before the mouse coordinates in the external file in the format: label/img_name
    """

    global num_clicks
    left_path = os.path.join(images_path, 'left')
    right_path = os.path.join(images_path, 'right')

    images_list = [img for img in os.listdir(images_path)]
    #images_list.sort()

    index = 0

    window = "image"
    cv2.namedWindow(window)

    file = open(file_path, "a")
    
    # Display the images
    for index in range(len(images_list)):

        current_image = images_list[index]
        image = cv2.imread(images_path + '/' + current_image)

        image_l = left_half(image)
        image_l = cv2.putText(image_l, current_image, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        image_r = right_half(image)
        image_r = cv2.putText(image_r, current_image, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        selector = PixelSelector(image_l, image_r, stereo_params)
        xl1, xr1, y1 = selector.run()
        print('f')
        selector = PixelSelector(image_l, image_r, stereo_params)
        xl2, xr2, y2 = selector.run()
        
        print(f' {xl1} {y1} {xl2} {y2}')
        print(f' {xr1} {y1} {xr2} {y2}')

        file.write('left/' + current_image + f' {xl1} {y1} {xl2} {y2}\n')
        file.write('right/' + current_image + f' {xr1} {y1} {xr2} {y2}\n')

    file.close()


file_name = "right.txtdddddddddddd" 
file_path = os.path.join(data_path, "stereo", "dualcam-potted-pool") 

#browse_images(file_path, left_images, "left")
browse_images(os.path.join(file_path, 'test.txt'), file_path, StereoParameters.load('stereo-pool'), "right")
