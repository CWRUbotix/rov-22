import math
import statistics
import re
from collections import defaultdict

STEREO_BASELINE = 4  # cm
FOCAL_LENGTH = 0.1  # cm, just a guess because the undistortion process probably screws with this
RESOLUTION_X = 640
RESOLUTION_Y = 480

LEFT_FX = 261.94794306446124
LEFT_FY = 261.4785138907309
LEFT_CX = 325.3871656152444
LEFT_CY = 231.51814888773677

RIGHT_FX = 253.5047592756691
RIGHT_FY = 253.76547695471558
RIGHT_CX = 337.0384349728359
RIGHT_CY = 235.03841855879503


def pixel_to_film_coords(point, fx, fy, cx, cy):
    return (
        (point[0] - cx) / fx,
        (point[1] - cy) / fy
    )


def get_point_camera_space(p1, p2):
    film_coord1 = pixel_to_film_coords(p2, LEFT_FX, LEFT_FY, LEFT_CX, LEFT_CY)
    film_coord2 = pixel_to_film_coords(p1, RIGHT_FX, RIGHT_FY, RIGHT_CX, RIGHT_CY)
    #print(str(film_coord1) + ',  ' + str(film_coord2))

    disparity = film_coord2[0] - film_coord1[0]
    depth = FOCAL_LENGTH * STEREO_BASELINE / disparity

    return (
        film_coord1[0] * STEREO_BASELINE / disparity,
        film_coord1[1] * STEREO_BASELINE / disparity,
        depth
    )


if __name__ == "__main__":
    with open("../data/stereo/fish_pixels_list") as data_file:
        test_dict = defaultdict(lambda: {})

        for line in data_file.read().split("\n"):
            fname, x1, y1, x2, y2 = line.split(" ")
            match = re.match(r"(\w+)/(\d+)", fname)
            test_dict[match[2]][match[1]] = ((int(x1), int(y1)), (int(x2), int(y2)))

        for k in list(test_dict.keys()):
            if len(test_dict[k].keys()) != 2:
                test_dict.pop(k)

        fish_lengths = []
        for k, v in test_dict.items():
            left_points = v["left"]
            right_points = v["right"]

            point1 = get_point_camera_space(left_points[0], right_points[0])
            point2 = get_point_camera_space(left_points[1], right_points[1])
            #print(point1, point2)

            fish_lengths.append(math.dist(point1, point2))
            #print(point2[0] - point1[0])
            #print(math.dist(point1, point2))

        mean = statistics.mean(fish_lengths)
        std_dev = statistics.pstdev(fish_lengths)
        print(f"Mean: {mean}")
        print(FOCAL_LENGTH, f"Std Dev: {std_dev} ({round(std_dev/mean*100)}%)")
