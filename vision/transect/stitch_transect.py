import cv2
import imutils
from vision.transect.transect_image import TransectImage
from vision.colors import *
from vision.transect.line import *

class StitchTransect():

    def __init__(self):
        self.images = dict.fromkeys([0, 1, 2, 3, 4, 5, 6, 7], TransectImage)

    def set_image(self, key, trans_img):
        # If the image is horizontal, flip it to be vertical
        # TEMPORARY FIX DELETE BEFORE COMPETITION
        height, width, _ = trans_img.image.shape

        if width > height:
            trans_img.image = cv2.rotate(trans_img.image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.images[key] = trans_img

    def get_images(self):
        image_list = []
        
        for key in self.images:
            image_list.append(self.images[key].image)

        return image_list

stitcher_test = StitchTransect()

def cropped_images(stitcher, debug=False):
    """
    
    """

    cropped = []

    for key in stitcher.images:
        trans_img = stitcher.images[key]
        coords = trans_img.coords

        # Figure out which coordinate is for which corner
        coords.sort(key=lambda coord: coord[1])
        
        upper = [coords[0], coords[1]]
        lower = [coords[2], coords[3]]

        upper.sort(key=lambda coord: coord[0])
        lower.sort(key=lambda coord: coord[0])

        x1, y1 = upper[0] # top left
        x2, y2 = upper[1] # top right
        x3, y3 = lower[0] # bottom left
        x4, y4 = lower[1] # bottom right

        if debug:
            image = cv2.circle(image, (x1, y1), radius=0, color=(0, 255, 0), thickness=50)
            image = cv2.circle(image, (x2, y2), radius=0, color=(0, 255, 0), thickness=50)
            image = cv2.circle(image, (x3, y3), radius=0, color=(0, 255, 0), thickness=50)
            image = cv2.circle(image, (x4, y4), radius=0, color=(0, 255, 0), thickness=50)

        # Warp image 
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

def final_stitched_image(cropped):
    """
    
    """
    
    cropped[2], cropped[3] = cropped[3], cropped[2]
    cropped[6], cropped[7] = cropped[7], cropped[6]

    height, width, _ = cropped[0].shape

    final_height = height * 4
    final_width = width * 2

    final_image = np.zeros((final_height, final_width, 3), np.uint8) 
    print(final_image.shape)

    # Start from bottom left of final image
    id = 0
    y = final_height

    for i in range(4):
        x = 0
        for j in range(2):
            final_image[y-height:y, x:x+width] = cropped[id]

            x += width
            id += 1
        y -= height

    return final_image

