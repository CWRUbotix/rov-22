import numpy as np

print('Input current speed, current direction, and time: ')
currentSpeed, currentDirection, time = float(input()), float(input()), float(input())

angleRad = currentDirection * np.pi/180
timeSeconds = time * 3600
currentDistance = currentSpeed * timeSeconds / 1000

horizontalDistance = currentDistance * np.sin(angleRad)
verticalDistance = currentDistance * np.cos(angleRad)

horizontalPixels = horizontalDistance / 2
verticalPixels = verticalDistance / 2

print('VerticalDistance: {} km'.format(round(verticalDistance, 2)))
print('HorizontalDistance: {} km'.format(round(horizontalDistance, 2)))
print('VerticalPixels: {} squares'.format(int(verticalPixels)))
print('HorizontalPixels: {} squares'.format(int(horizontalPixels)))
print('Negative is West and South')