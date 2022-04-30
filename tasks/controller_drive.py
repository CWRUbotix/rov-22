from PyQt5.QtCore import Qt
from tasks.base_task import BaseTask
from vehicle.vehicle_control import VehicleControl, InputChannel, BACKWARD_CAM_INDICES
from controller.controller import XboxController


class ControllerDrive(BaseTask):
    """
    Control thrusters via keyboard

    Controls:
    WASD: Forward and lateral translation
    Control: Down
    Shift: Up (I couldn't use space because PyQt already uses it  and for some stupid reason I couldn't override it)
    IJKL: Pitch and Yaw
    U/O: Roll
    """
    def __init__(self, vehicle: VehicleControl, controller: XboxController, get_video_index):
        self.controller = controller
        self.get_video_index = get_video_index
        super().__init__(vehicle)

    def initialize(self):
        self.vehicle.stop_thrusters()

    def periodic(self):
        """Set vehicle inputs based on controller inputs"""
        inputs = self.controller.get_vehicle_inputs()

        if self.get_video_index() in BACKWARD_CAM_INDICES:
            for channel in (InputChannel.FORWARD, InputChannel.LATERAL, InputChannel.PITCH, InputChannel.ROLL):
                inputs[channel] *= -1


        self.vehicle.set_rc_inputs(inputs)

    def end(self):
        self.vehicle.stop_thrusters()
