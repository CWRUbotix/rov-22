import math
import statistics
import re
from collections import defaultdict

STEREO_BASELINE = 10  # cm
FOCAL_LENGTH = 0.15  # cm, just a guess because the undistortion process probably screws with this
RESOLUTION_X = 640
RESOLUTION_Y = 480


def pixel_to_film_coords(point):
    return (
        point[0] / RESOLUTION_X - 0.5,
        point[1] / RESOLUTION_X - 0.5
    )


def get_point_camera_space(p1, p2):
    film_coord1 = pixel_to_film_coords(p1)
    film_coord2 = pixel_to_film_coords(p2)

    disparity = abs(film_coord2[0] - film_coord1[0])
    depth = FOCAL_LENGTH * STEREO_BASELINE / disparity

    return (
        film_coord1[0] * depth / FOCAL_LENGTH,
        film_coord2[0] * depth / FOCAL_LENGTH,
        depth
    )


if __name__ == "__main__":
    with open("../../data/stereo/fish_pixels_list") as data_file:
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
            print(point1, point2)

            fish_lengths.append(math.dist(point1, point2))

        mean = statistics.mean(fish_lengths)
        std_dev = statistics.pstdev(fish_lengths)
        print(f"Mean: {mean}")
        print(FOCAL_LENGTH, f"Std Dev: {std_dev} ({round(std_dev/mean*100)}%)")
