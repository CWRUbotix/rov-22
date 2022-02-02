import time
import typing as t

from PyQt5.QtCore import QThread

from vehicle.vehicle_control import VehicleControl
from logger import root_logger
from tasks.base_task import BaseTask


PERIODIC_FREQUENCY = 30

logger = root_logger.getChild(__name__)


class TaskScheduler(QThread):
    def __init__(self, vehicle: VehicleControl):
        super().__init__()
        self.vehicle = vehicle
        self.current_task: t.Optional[BaseTask] = None
        self.default_task: t.Optional[BaseTask] = None

    def start_task(self, task: BaseTask):
        if self.vehicle.is_connected() and self.vehicle.is_armed():
            self.end_current_task()
            self.current_task = task
            task.initialize()
            logger.info(f"Started task \"{str(task)}\"")

    def end_current_task(self):
        if self.current_task is not None:
            self.current_task.end()
            self.current_task = None

    def run(self):
        last_timestamp = time.time_ns()
        period_ns = int(1e9) // PERIODIC_FREQUENCY

        while True:
            self.vehicle.update()

            if not self.vehicle.is_connected() or not self.vehicle.is_armed():
                self.end_current_task()
            else:
                if self.current_task is None and self.default_task is not None:
                    self.start_task(self.default_task)

                if self.current_task is not None:
                    self.current_task.periodic()
                    if self.current_task.is_finished():
                        logger.info(f"Task \"{str(self.current_task)}\" finished")
                        self.end_current_task()

            wait_until = last_timestamp + period_ns
            current_time = time.time_ns()

            # Don't run more than PERIODIC_FREQUENCY times a second
            if current_time < wait_until:
                last_timestamp += period_ns
                self.msleep((wait_until - current_time) // 1000000)
            else:
                logger.debug(f"Scheduler loop overrun of {(current_time - wait_until) // 1000000}ms")
                last_timestamp = current_time

    def get_current_task_name(self) -> str:
        return "None" if self.current_task is None else str(self.current_task)
