from PyQt5.QtCore import Qt
from tasks.base_task import BaseTask
from vehicle.vehicle_control import VehicleControl, InputChannel

TRANSLATION_SENSITIVITY = 0.2
ROTATIONAL_SENSITIVITY = 1.0


class KeyboardControl(BaseTask):
    """
    Control thrusters via keyboard

    Controls:
    WASD: Forward and lateral translation
    Shift: Down
    Space: Up
    IJKL: Pitch and Yaw
    U/O: Roll
    """
    def __init__(self, vehicle: VehicleControl, keys_down):
        super().__init__(vehicle)
        self.keys_down = keys_down

    def initialize(self):
        self.vehicle.stop_thrusters()

    def periodic(self):
        """Set vehicle inputs based on pressed keys"""
        inputs = {
            InputChannel.FORWARD: (self.keys_down[Qt.Key_W] - self.keys_down[Qt.Key_S]) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL: (self.keys_down[Qt.Key_D] - self.keys_down[Qt.Key_A]) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.keys_down[Qt.Key_Space] - self.keys_down[Qt.Key_Shift]) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH: (self.keys_down[Qt.Key_I] - self.keys_down[Qt.Key_K]) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW: (self.keys_down[Qt.Key_L] - self.keys_down[Qt.Key_J]) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL: (self.keys_down[Qt.Key_U] - self.keys_down[Qt.Key_O]) * ROTATIONAL_SENSITIVITY,
        }

        self.vehicle.set_rc_inputs(inputs)

    def end(self):
        self.vehicle.stop_thrusters()
