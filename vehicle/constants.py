from enum import Enum


class Camera(Enum):
    FRONT = 'front'
    BACK = 'back'
    BOTTOM = 'bottom'
    DUAL = 'dual'


CAM_INDICES = {
    Camera.FRONT: 0,
    Camera.BOTTOM: 1,
    Camera.DUAL: 2,
}

BACKWARD_CAM_INDICES = ()  # Empty tuple


class InputChannel(Enum):
    PITCH = 1
    ROLL = 2
    THROTTLE = 3  # Translation on the Z axis
    YAW = 4
    FORWARD = 5
    LATERAL = 6
    PAN_CAMERA = 7
    TILT_CAMERA = 8
    LIGHTS_1 = 9
    LIGHTS_2 = 10
    VIDEO_SWITCH = 11


class Relay(Enum):
    PVC_FRONT = 0  # Hardware pin
    CLAW_FRONT = 1
    PVC_BACK = 2
    CLAW_BACK = 3
    MAGNET = 4
    LIGHTS = 5
