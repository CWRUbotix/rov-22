import math
import numpy as np
import cv2
from scipy.optimize import curve_fit

def vertical_edge(img):
    grad = cv2.Sobel(img, -1, dx=1, dy=0, ksize=3)
    return np.linalg.norm(grad, axis=2).astype(dtype='uint8')


def refine_coords(image_l, image_r, xl, xr, y, neighborhood_size=9):
    template = image_l[y - neighborhood_size: y + neighborhood_size, xl - neighborhood_size: xl + neighborhood_size + 1]
    search_area = image_r[y - neighborhood_size: y + neighborhood_size, xr - 2 * neighborhood_size: xr + 2 * neighborhood_size + 1]

    # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # search_area = cv2.cvtColor(search_area, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(max_loc)

    cv2.imshow('Template', template)
    cv2.imshow('Search', search_area)
    cv2.imshow('Result', res)
    cv2.waitKey(1)

    return xl, xr - neighborhood_size + max_loc[0], y


def gaussian(x, mean, std, scale):
    return scale * np.exp((- np.square((x - mean)) / std))

def fit_gaussian(xvals, yvals):
    max_idx = -1
    max_val = 0
    for idx, val in enumerate(yvals):
        if val > max_val:
            max_val = val
            max_idx = idx
    
    init_guess = [xvals[max_idx], 5, max_val]

    bounds = ([min(xvals), 0.01, max_val / 2], [max(xvals), 1000, max_val * 2])

    opt, _ = curve_fit(gaussian, xvals, yvals, p0=init_guess, bounds=bounds)
    return opt


if __name__ == '__main__':
    xvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    yvals = [22, 21, 22, 31, 47, 65, 87, 107, 116, 113, 101, 84, 65, 47, 34, 25, 20, 17, 18]

    print(fit_gaussian(xvals, yvals))