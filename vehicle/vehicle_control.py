import enum
import time
import typing as t
from pymavlink import mavutil

from logger import root_logger

logger = root_logger.getChild(__name__)


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


class VehicleControl:
    def __init__(self, port):
        self.last_heartbeat = None
        self.connected = False

        self.link = mavutil.mavlink_connection(f'udpin:0.0.0.0:{port}')

    def check_heartbeat(self) -> None:
        if self.link.wait_heartbeat(blocking=False) is not None:
            self.last_heartbeat = time.time()

    def arm(self) -> None:
        self.link.arducopter_arm()
        logger.info("Arm command sent")

    def disarm(self) -> None:
        self.link.arducopter_disarm()
        logger.info("Disarm command sent")

    def is_connected(self) -> bool:
        last_connected = self.connected
        self.connected = self.last_heartbeat is not None and time.time() - self.last_heartbeat < 2  # Timeout after 2 seconds
        if not last_connected and self.connected:
            logger.debug("Connected to vehicle")
        elif last_connected and not self.connected:
            logger.info("Lost connection to vehicle")
        return self.connected

    def is_armed(self) -> bool:
        return self.link.motors_armed()

    def set_rc_input_pwms(self, pwms: t.Dict[int, int]) -> None:
        """Sets and RC input channel pwm value. PWM values should be between 1100 and 1900"""
        if not self.is_connected() or not self.is_armed():
            return

        rc_channel_values = [65535] * 18  # 65535 Means "ignore this field"

        for channel_id, pwm in pwms.items():
            if channel_id < 1 or channel_id > 18:
                raise ValueError(f"Channel id does not exist: {channel_id}")

            if not 1100 <= pwm <= 1900:
                raise ValueError(f"PWM values must be between 1100 and 1900, not f{pwm}")

            rc_channel_values[channel_id - 1] = pwm

        self.link.mav.rc_channels_override_send(
            self.link.target_system,  # target_system
            self.link.target_component,  # target_component
            *rc_channel_values  # RC channel list, in microseconds.
        )

    def set_rc_inputs(self, values: t.Dict[InputChannel, float]) -> None:
        """Sets inputs to the pixhawk using values between -1 (full reverse) and 1 (full forward)"""
        pwms = {}
        for channel, val in values.items():
            if not -1 <= val <= 1:
                raise ValueError(f"Inputs must be between -1 and 1, not {val}")

            pwm = round(val * 400 + 1500)
            pwm = min(max(pwm, 1100), 1900)  # Clamp to acceptable pwm range in case of float weirdness
            pwms[channel.value] = pwm

        self.set_rc_input_pwms(pwms)

    def stop_thrusters(self) -> None:
        self.set_rc_inputs({
            InputChannel.FORWARD: 0,
            InputChannel.LATERAL: 0,
            InputChannel.THROTTLE: 0,
            InputChannel.YAW: 0,
            InputChannel.PITCH: 0,
            InputChannel.ROLL: 0,
        })
        logger.debug("Thrusters stopped")
