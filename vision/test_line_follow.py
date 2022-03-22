#import the libraries
import cv2 as cv
import numpy as np

#read the image
img = cv.imread("D:/Rov 22/rov-vision-22/vision/red scarf.jpg")

#convert the BGR image to HSV colour space
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

#set the lower and upper bounds for the green hue
lower_red = np.array([160,100,50])
upper_red = np.array([180,255,255])

#create a mask for green colour using inRange function
mask = cv.inRange(hsv, lower_red, upper_red)

mask_inv = cv.bitwise_not(mask)

#perform bitwise and on the original image arrays using the mask
res = cv.bitwise_and(img, img, mask=mask)

background = cv.bitwise_and(gray, gray, mask = mask_inv)
background = np.stack((background,)*3, axis=-1)
added_img = cv.add(res, background)
#create resizable windows for displaying the images
cv.namedWindow("res", cv.WINDOW_NORMAL)
cv.namedWindow("hsv", cv.WINDOW_NORMAL)
cv.namedWindow("mask", cv.WINDOW_NORMAL)
cv.namedWindow("added", cv.WINDOW_NORMAL)
cv.namedWindow("back", cv.WINDOW_NORMAL)
cv.namedWindow("mask_inv", cv.WINDOW_NORMAL)
cv.namedWindow("gray", cv.WINDOW_NORMAL)

#display the images
cv.imshow("back", background)
cv.imshow("mask_inv", mask_inv)
cv.imshow("added",added_img)
cv.imshow("mask", mask)
cv.imshow("gray", gray)
cv.imshow("hsv", hsv)
cv.imshow("res", res)

if cv.waitKey(0):
    cv.destroyAllWindows()