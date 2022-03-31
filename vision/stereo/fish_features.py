import math
import numpy as np
import cv2
from scipy.optimize import curve_fit

def vertical_edge(img):
    grad = cv2.Sobel(img, -1, dx=1, dy=0, ksize=3)
    return np.linalg.norm(grad, axis=2).astype(dtype='uint8')


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