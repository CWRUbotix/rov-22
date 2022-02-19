import math
import statistics
import re
from collections import defaultdict

STEREO_BASELINE = 6  # cm
FOCAL_LENGTH = 500  # cm, just a guess because the undistortion process probably screws with this
RESOLUTION_X = 1280
RESOLUTION_Y = 960

FX = 500
FY = 500
CX = 640
CY = 480

ACTUAL = 32


def pixel_to_film_coords(point, fx, fy, cx, cy):
    return (
        (point[0] - cx) ,
        (point[1] - cy)
    )


def get_point_camera_space(p1, p2):
    film_coord1 = pixel_to_film_coords(p1, FX, FY, CX, CY)
    film_coord2 = pixel_to_film_coords(p2, FX, FY, CX, CY)
    #print(str(film_coord1) + ',  ' + str(film_coord2))

    disparity = film_coord2[0] - film_coord1[0]
    depth = FOCAL_LENGTH * STEREO_BASELINE / disparity

    return (
        film_coord1[0] * STEREO_BASELINE / disparity,
        film_coord1[1] * STEREO_BASELINE / disparity,
        depth
    )


if __name__ == "__main__":
    with open("../data/stereo/gazebo1/pixels.txt") as data_file:
        test_dict = defaultdict(lambda: {})

        for line in data_file.read().split("\n"):
            fname, x1, y1, x2, y2 = line.split(" ")
            match = re.match(r"(\w+)/(\d+)", fname)
            test_dict[match[2]][match[1]] = ((int(x1), int(y1)), (int(x2), int(y2)))

        for k in list(test_dict.keys()):
            if len(test_dict[k].keys()) != 2:
                test_dict.pop(k)

        x_diffs = []
        fish_lengths = []
        for k, v in test_dict.items():
            left_points = v["left"]
            right_points = v["right"]

            point1 = get_point_camera_space(left_points[0], right_points[0])
            point2 = get_point_camera_space(left_points[1], right_points[1])
            #print(point1, point2)

            x_diffs.append(point1[0] - point2[0])
            fish_lengths.append(math.dist(point1, point2) - ACTUAL)
            #print(point2[0] - point1[0])
            print(f'{point1[0] - point2[0]} ,  {math.dist(point1, point2)}')

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
        plt.hlines(-2, 0, max(x_diffs))
        plt.hlines(2, 0, max(x_diffs))
        plt.show()

