from PyQt5.QtCore import Qt
from tasks.base_task import BaseTask
from vehicle.constants import InputChannel, BACKWARD_CAM_INDICES
from vehicle.vehicle_control import VehicleControl

TRANSLATION_SENSITIVITY = 0.2
ROTATIONAL_SENSITIVITY = 1.0


class KeyboardControl(BaseTask):
    """
    Control thrusters via keyboard

    Controls:
    WASD: Forward and lateral translation
    Control: Down
    Shift: Up (I couldn't use space because PyQt already uses it  and for some stupid reason I couldn't override it)
    IJKL: Pitch and Yaw
    U/O: Roll
    """
    def __init__(self, vehicle: VehicleControl, keys_down, get_video_index):
        super().__init__(vehicle)
        self.keys_down = keys_down
        self.get_video_index = get_video_index

    def initialize(self):
        self.vehicle.stop_thrusters()

    def periodic(self):
        """Set vehicle inputs based on pressed keys"""
        # Possible values for each input: -sensitivity, 0, +sensitivity
        inputs = {
            InputChannel.FORWARD:  (self.keys_down[Qt.Key_W] - self.keys_down[Qt.Key_S]) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL:  (self.keys_down[Qt.Key_D] - self.keys_down[Qt.Key_A]) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.keys_down[Qt.Key_Shift] - self.keys_down[Qt.Key_Control]) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH:    (self.keys_down[Qt.Key_I] - self.keys_down[Qt.Key_K]) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW:      (self.keys_down[Qt.Key_L] - self.keys_down[Qt.Key_J]) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL:     (self.keys_down[Qt.Key_O] - self.keys_down[Qt.Key_U]) * ROTATIONAL_SENSITIVITY,
        }

        if self.get_video_index() in BACKWARD_CAM_INDICES:
            for channel in (InputChannel.FORWARD, InputChannel.LATERAL, InputChannel.PITCH, InputChannel.ROLL):
                inputs[channel] *= -1

        self.vehicle.set_rc_inputs(inputs)

    def end(self):
        self.vehicle.stop_thrusters()
