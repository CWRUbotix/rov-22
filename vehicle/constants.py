import enum

FRONT_CAMERA_INDEX = 0
BOTTOM_CAMERA_INDEX = 1
BACK_CAMERA_INDEX = 2

BACKWARD_CAM_INDICES = (2,)


class InputChannel(enum.Enum):
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


class Relay(enum.Enum):
    PVC_FRONT = 0  # Hardware pin
    CLAW_FRONT = 1
    PVC_BACK = 2
    CLAW_BACK = 3
    MAGNET = 4
    LIGHTS = 5
