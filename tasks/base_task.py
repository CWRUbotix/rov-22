from vehicle.vehicle_control import VehicleControl
from gui.data_classes import Frame


class BaseTask:
    """A base class which should be subclassed by each task to be used with the Scheduler"""
    def __init__(self, vehicle: VehicleControl):
        self.vehicle = vehicle

    def initialize(self):
        """Called once whenever the task is (re)started"""
        pass

    def periodic(self):
        """Called periodically while the task is running"""
        pass

    def end(self):
        """Called once when the task finishes or is cancelled"""
        pass

    def is_finished(self) -> bool:
        """Called periodically when the task is running. If this returns true, the task will be cancelled"""
        return False

    def handle_frame(self, frame: Frame):
        """Called whenever a new frame is received from a camera"""
        pass

    def __str__(self) -> str:
        """Get a readable name of the task"""
        return type(self).__name__
