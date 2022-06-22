import math
from os import path
import statistics
import re
from collections import defaultdict
from vision.stereo.stereo_util import Side
from vision.stereo.fish_features import refine_coords
import cv2
from vision.stereo.params import StereoParameters

STEREO_BASELINE = 2.375  # cm
FOCAL_LENGTH = 1150  # cm, just a guess because the undistortion process probably screws with this
RESOLUTION_X = 1280
RESOLUTION_Y = 960

FX = FOCAL_LENGTH
FY = FOCAL_LENGTH
CX = 640
CY = 480

ACTUAL = 31


def pixel_to_film_coords(point, fx, fy, cx, cy):
    return (
        (point[0] - cx) / fx ,
        (point[1] - cy) / fy
    )


def get_point_camera_space(p1, p2):
    film_coord1 = pixel_to_film_coords(p1, 1155, 1155, 687.588, 535.241)
    film_coord2 = pixel_to_film_coords(p2, 1142, 1142, 702.712, 503.471)
    #print(str(film_coord1) + ',  ' + str(film_coord2))

    disparity = film_coord2[0] - film_coord1[0]
    depth =  STEREO_BASELINE / disparity

    return (
        film_coord1[0] * STEREO_BASELINE / disparity,
        film_coord1[1] * STEREO_BASELINE / disparity,
        depth
    )


if __name__ == "__main__":
    params = StereoParameters.load('stereo-pool')

    with open("../data/stereo/dualcam-potted-pool/test.txt") as data_file:
        test_dict = defaultdict(lambda: {})

        for line in data_file.read().split("\n"):
            fname, x1, y1, x2, y2 = line.split(" ")
            match = re.match(r"(\w+)/(\S+).png", fname)
            test_dict[match[2]][match[1]] = ((int(x1), int(y1)), (int(x2), int(y2)))

        for k in list(test_dict.keys()):
            if len(test_dict[k].keys()) != 2:
                test_dict.pop(k)

        x_diffs = []
        fish_lengths = []
        for k, v in test_dict.items():
            left_points = v["left"]
            right_points = v["right"]
            # print(f'../data/stereo/dualcam1filtered/left/{k}.png')
            # img_l = cv2.imread(f'../data/stereo/dualcam1filtered/left/{k}.png')
            # img_r = cv2.imread(f'../data/stereo/dualcam1filtered/right/{k}.png')

            # img_l = params.rectify_single(img_l, Side.LEFT)
            # img_r = params.rectify_single(img_r, Side.RIGHT)

            # img_l = cv2.GaussianBlur(img_l, (15, 15), 0)
            # img_r = cv2.GaussianBlur(img_r, (15, 15), 0)
            

            # point1 = get_point_camera_space(left_points[0], right_points[0])
            # point2 = get_point_camera_space(left_points[1], right_points[1])

            point1 = params.triangulate(left_points[0], right_points[0])
            point2 = params.triangulate(left_points[1], right_points[1])
            
            # xl1, xr1, y1 = refine_coords(img_l, img_r, left_points[0][0], right_points[0][0], left_points[0][1])
            # point1 = params.triangulate((xl1, y1), (xr1, y1))

            # xl2, xr2, y2 = refine_coords(img_l, img_r, left_points[1][0], right_points[1][0], left_points[1][1])
            # point2 = params.triangulate((xl2, y2), (xr2, y2))
            #print(point1, point2)

            x_diffs.append(point2[0] - point1[0])
            #dist = math.dist(point1, point2) * 1.6909861571441303
            dist = math.dist(point1, point2) * 2.126447913752668
            fish_lengths.append(dist)
            #print(point2[0] - point1[0])
            #print(f'{point1[0] - point2[0]} ,  {math.dist(point1, point2)}')
            print()

        mean = statistics.mean(fish_lengths)
        std_dev = statistics.pstdev(fish_lengths)
        print(f"Mean: {mean}")
        print(FOCAL_LENGTH, f"Std Dev: {std_dev} ({round(std_dev/mean*100)}%)")

        num_close = 0
        for length in fish_lengths:
            if abs(length - ACTUAL) <= 2:
                num_close += 1
        
        print(f"Num within 2cm: {num_close/len(fish_lengths)}")
        print(len(fish_lengths))

        import matplotlib.pyplot as plt
        plt.scatter(x_diffs, fish_lengths)
        plt.hlines(ACTUAL - 2, 0, max(x_diffs))
        plt.hlines(ACTUAL + 2, 0, max(x_diffs))
        plt.show()

