import cv2
import os
import imutils
from util import data_path
from vision.colors import *
from vision.transect.line import *
from vision.transect.stitch_transect import *

def cropped_images(debug=False):

    cropped = []

    for key in stitcher.images:
        trans_img = stitcher.images[key]
        coords = trans_img.coords

        if len(coords) != 4:
            raise Exception("Must have 4 coords")

        coords.sort(key=lambda coord: coord[1])
            
        upper = [coords[0], coords[1]]
        lower = [coords[2], coords[3]]

        upper.sort(key=lambda coord: coord[0])
        lower.sort(key=lambda coord: coord[0])

        x1, y1 = upper[0] # top left
        x2, y2 = upper[1] # top right
        x3, y3 = lower[0] # bottom left
        x4, y4 = lower[1] # bottom right

        image = trans_img.image
        height, width, _ = image.shape

        src = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        dst = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        matrix = cv2.getPerspectiveTransform(src, dst)
        
        # Perspective transform original image
        warped = cv2.warpPerspective(image, matrix, (width, height))

        resized = imutils.resize(warped, width=400)        
        cropped.append(resized)

        if debug:
            cv2.imshow('warped', resized)
            cv2.waitKey(0)

    return cropped

def record_mouse_position(event, x, y, flags, param):
    """

    """ 

    trans = param[0]

    # Get mouse coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        trans.coords.append((x, y))
        print(f"Square {trans.num} coord {len(trans.coords)}: ({x}, {y})")

def select_intersections():
    """
    Let's you browse through the transect images and select the 4 corners of each rectangle.

    'a' key to go back
    'd' key to go forwards
    'r' key to reset intersection points
    'esc' to exit

    @return: true if you selected 4 corners for all 8 squares, otherwise false
    """

    # folder_path = os.path.join(data_path, "transect", "stitching", "p00l")

    # files = [img_name for img_name in os.listdir(folder_path)]
    # files.sort()

    # images_list = [cv2.imread(os.path.join(folder_path, img)) for img in files]

    images_list = []

    for key in stitcher.images:
        images_list.append(stitcher.images[key].image)

    index = 0

    window = "window"
    cv2.namedWindow(window)
    
    # Display the images
    while True:

        curr_image = images_list[index]
        curr_trans = stitcher.images[index+1]

        text = f"Square {index+1}"

        curr_image = cv2.putText(curr_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window, curr_image)

        cv2.setWindowProperty(window, cv2.WND_PROP_TOPMOST, 1)
        cv2.setMouseCallback(window, record_mouse_position, [curr_trans])

        k = cv2.waitKey(0) & 0xFF

        # 'a' key to go back    
        if k == 97 and index > 0:
            index -= 1

        # 'd' key to go forwards
        elif k == 100 and index < len(images_list) - 1: 
            index += 1

        # 'r' key to reset transect coords
        elif k == 114:
            curr_trans.coords = []

        # 'esc' to quit
        elif k == 27 or k == 100: 
            cv2.destroyAllWindows()
            break

    # Verify that all transect images had 4 points set
    for key in stitcher.images:
        if len(stitcher.images[key].coords) != 4:
            return False

    return True

def stitch_manually():
    if not select_intersections():
        print("Exiting")
        return

    print("Continuing")
    cropped = cropped_images()
