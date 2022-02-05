"""Goes through the fish images for manually marking the ends of the fish"""

import cv2
import os
import shutil
from util import data_path    

file_path = "/Users/georgiamartinez/rov-vision-22/scripts/fish_pixels_list"

file = open(file_path, "a")
num_clicks = 0

def record_mouse_position(event, x, y, flags, param):
    """Records mouse position on click""" 

    global num_clicks

    label = param[0]
    image_name = label+"/"+param[1]

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

def browse_images(label):
    """Browse images with the 'a' and 'd' keys"""

    global file, num_clicks

    # Get list of images to browse through
    image_path = os.path.join(data_path, "stereo", "1undistort", label)

    images_list = [img for img in os.listdir(image_path)]
    images_list.sort()

    index = 0

    window = "image"
    cv2.namedWindow(window)
    
    # Display the images
    while True:

        current_image = images_list[index]

        image = cv2.imread(image_path +"/"+ current_image)
        image = cv2.putText(image, current_image, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window, image)

        cv2.setWindowProperty(window, cv2.WND_PROP_TOPMOST, 1)
        cv2.setMouseCallback(window, record_mouse_position, [label, current_image])

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

def save_to_data():
    """Saves file to data repo"""

    shutil.move(file_path, data_path + "/stereo/fish_pixels_list")

# browse_images("left")
# browse_images("right")

file.close()