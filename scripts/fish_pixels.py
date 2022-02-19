"""Goes through the fish images for manually marking the ends of the fis"""

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

def browse_images(file_path, images_path, label=""):
    """
    Browse through images with the 'a' and 'd' keys

    :param file_path: path to text file to write the coordinates to
    :param images_path: path to the images to look through
    :param label: optional text printed before the mouse coordinates in the external file in the format: label/img_name
    """

    global num_clicks
    images_list = [img for img in os.listdir(images_path)]
    images_list.sort()

    index = 0

    window = "image"
    cv2.namedWindow(window)

    file = open(file_path, "a")
    
    # Display the images
    while True:

        current_image = images_list[index]

        image = cv2.imread(images_path +"/"+ current_image)
        image = cv2.putText(image, current_image, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window, image)

        cv2.setWindowProperty(window, cv2.WND_PROP_TOPMOST, 1)
        cv2.setMouseCallback(window, record_mouse_position, [file, label, current_image])

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

    file.close()


file_name = "right.txtdddddddddddd" 
file_path = os.path.join(data_path, "stereo", "gazebo1", file_name) 

left_images = os.path.join(data_path, "stereo", "gazebo1", "left")
right_images = os.path.join(data_path, "stereo", "gazebo1", "right")

#browse_images(file_path, left_images, "left")
browse_images(file_path, right_images, "right")
