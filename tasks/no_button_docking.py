import time

from tasks.base_task import BaseTask
from vehicle.vehicle_control import VehicleControl, InputChannel

FORWARD_SPEED = 0.08
TASK_DURATION = 5


class NoButtonDocking(BaseTask):
    """
    Fly forward at a constant speed for a fixed amount of time
    """

    def __init__(self, vehicle: VehicleControl):
        super().__init__(vehicle)
        self.start_time = None

    def initialize(self):
        self.start_time = time.time()

    def periodic(self):
        inputs = {
            InputChannel.FORWARD:  FORWARD_SPEED,
        }
        self.vehicle.set_rc_inputs(inputs)

    def is_finished(self) -> bool:
        return time.time() >= self.start_time + TASK_DURATION

    def end(self):
        self.vehicle.stop_thrusters()
