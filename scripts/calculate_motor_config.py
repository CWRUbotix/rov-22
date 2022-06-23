import math
from typing import List, Tuple
import numpy as np

# Default Config
MOTOR_COORDS: List[Tuple[float, float, float]] = [
    (1, 1, 0),
    (-1, 1, 0),
    (1, -1, 0),
    (-1, -1, 0),
    (2, 1, 0),
    (-2, 1, 0),
    (2, -1, 0),
    (-2, -1, 0)]

MOTOR_DIRECTIONS: List[Tuple[float, float, float]] = [
    (1, -1, 0),
    (-1, -1, 0),
    (1, 1, 0),
    (-1, 1, 0),
    (0, 0, -1),
    (0, 0, -1),
    (0, 0, -1),
    (0, 0, -1)]


MOTOR_COORDS: List[Tuple[float, float, float]] = [
    (6.726, 9.27, 1.996),
    (-6.726, 9.27, 1.996),
    (6.726, -9.27, 1.996),
    (-6.726, -9.27, 1.996),
    (9.247, 4.127, 0),
    (-9.247, 4.127, 0),
    (9.247, -4.127, 0),
    (-9.247, -4.127, 0)]

angle = 40 * math.pi / 180

MOTOR_DIRECTIONS: List[Tuple[float, float, float]] = [
    (math.sin(angle), -math.cos(angle), 0),
    (-math.sin(angle), -math.cos(angle), 0),
    (math.sin(angle), math.cos(angle), 0),
    (-math.sin(angle), math.cos(angle), 0),
    (0, 0, -2.2),
    (0, 0, -2.2),
    (0, 0, -2.2),
    (0, 0, -2.2)]

for idx, (coords, direction) in enumerate(zip(MOTOR_COORDS, MOTOR_DIRECTIONS)):
    x, y, z = coords
    torque = np.cross(coords, direction) / 20

    print(f'add_motor_raw_6dof(AP_MOTORS_MOT_{idx+1}, {torque[1]}f, {torque[0]}f, {-torque[2]}f, {direction[2]}f, {direction[1]}f, {direction[0]}f, {idx+1});')
    
    