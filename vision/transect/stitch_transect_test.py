import cv2
import os
from util import data_path

from vision.transect.transect_image import TransectImage
from vision.transect.stitch_transect import StitchTransect

folder_A = os.path.join(data_path, "transect", "stitching", "A")

stitcher = StitchTransect()

for i in range(1, 9):

    subfolder_path = os.path.join(folder_A, str(i))
    image_name = os.listdir(subfolder_path)[0]
    complete_path = os.path.join(subfolder_path, image_name)

    image = TransectImage(i, cv2.imread(complete_path))

    stitcher.set_image(i, image)
