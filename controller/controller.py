import time
import typing as t
from abc import abstractmethod

from inputs import get_gamepad, devices
import math
import threading
from enum import Enum

from vehicle.constants import InputChannel, Relay, BACKWARD_CAM_INDICES

TRANSLATION_SENSITIVITY = 1
ROTATIONAL_SENSITIVITY = 0.75


def apply_curve(value, exponential):
    value = min(max(value, -1), 1)  # clamp the joystick input from -1 to 1
    return math.copysign(abs(value) ** exponential, value)


def map_range(val, base_range, new_range):
    return (val - base_range[0]) / (base_range[1] - base_range[0]) * (new_range[1] - new_range[0]) + new_range[0]


class Controller:
    class JoystickAxis(Enum):
        pass

    class Trigger(Enum):
        pass

    class Button(Enum):
        pass

    def __init__(self, get_big_video_index, joystick_curve_exponential=2, trigger_curve_exponential=2):
        self.JOY_RANGE = None
        self.TRIG_RANGE = None

        self.switch_camera_callbacks = []
        self.toggle_relay_callbacks = []

        self.get_big_video_index = get_big_video_index

        self.joystick_curve_exponential = joystick_curve_exponential
        self.trigger_curve_exponential = trigger_curve_exponential

        self.joystick_axes: t.Dict[Controller.JoystickAxis, float] = {}
        self.triggers: t.Dict[Controller.Trigger, float] = {}
        self.buttons: t.Dict[Controller.Button, bool] = {}

        self.joystick_axis_codes = [axis.value for axis in self.JoystickAxis]
        self.trigger_codes = [trigger.value for trigger in self.Trigger]
        self.button_codes = [button.value for button in self.Button]

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True

    def start_monitoring(self):
        self._monitor_thread.start()

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                self._handle_event(event)

    def _handle_event(self, event):
        code = event.code
        if "SYN" in code or code == "MSC_SCAN":
            return
        if code in self.joystick_axis_codes:
            self.joystick_axes[self.JoystickAxis(
                code)] = map_range(event.state, self.JOY_RANGE, (-1, 1))  # normalize between -1 and 1
        elif code in self.trigger_codes:
            self.triggers[self.Trigger(code)] = map_range(event.state, self.TRIG_RANGE, (0, 1))
        elif code in self.button_codes:
            self.buttons[self.Button(code)] = bool(event.state)
        else:
            print(f"Unrecognized: {code} {event.state}")

        self.check_for_camera_change(event)
        self.check_for_relay_toggle(event)

    def get(self, control: t.Union[JoystickAxis, Trigger, Button]) -> t.Union[float, bool]:
        if isinstance(control, self.JoystickAxis):
            return apply_curve(self.joystick_axes.get(control, 0), self.joystick_curve_exponential)
        if isinstance(control, self.Trigger):
            return apply_curve(self.triggers.get(control, 0), self.trigger_curve_exponential)
        if isinstance(control, self.Button):
            return self.buttons.get(control, False)

    @abstractmethod
    def get_vehicle_inputs(self):
        pass

    def register_camera_callback(self, callback):
        self.switch_camera_callbacks.append(callback)

    def call_camera_callbacks(self, index: int):
        for callback in self.switch_camera_callbacks:
            callback(index)

    def check_for_camera_change(self, event):
        """Process an event and call the switch camera callbacks if appropriate"""
        pass

    def register_relay_callback(self, relay: Relay, callback):
        self.toggle_relay_callbacks.append((relay, callback))

    def call_relay_callbacks(self, relay: Relay):
        for r, callback in self.toggle_relay_callbacks:
            if r == relay:
                callback()

    def check_for_relay_toggle(self, event):
        """Process an event and call the toggle relay callbacks if appropriate"""
        pass


class SteamController(Controller):
    def __init__(self, get_big_video_index):
        super().__init__(get_big_video_index)
        self.JOY_RANGE = (-32767, 32768)
        self.TRIG_RANGE = (0, 256)

    class JoystickAxis(Controller.JoystickAxis):
        ThumbstickX = "ABS_X"
        ThumbstickY = "ABS_Y"
        LeftPadX = "ABS_HAT0X"
        LeftPadY = "ABS_HAT0Y"
        RightPadX = "ABS_RX"
        RightPadY = "ABS_RY"

    class Trigger(Controller.Trigger):
        LeftTrigger = "ABS_HAT2Y"
        RightTrigger = "ABS_HAT2X"

    class Button(Controller.Button):
        LeftTrigger = "BTN_TL2"
        RightTrigger = "BTN_TR2"
        LeftBumper = "BTN_TL"
        RightBumper = "BTN_TR"
        A = "BTN_SOUTH"
        X = "BTN_NORTH"
        Y = "BTN_WEST"
        B = "BTN_EAST"
        Back = "BTN_SELECT"
        Start = "BTN_START"
        LeftPadTouch = "BTN_THUMB"
        RightPadTouch = "BTN_THUMB2"
        RightPadClick = "BTN_THUMBR"
        RightPad = "BTN_THUMB2-"
        DPadLeft = "BTN_DPAD_LEFT"
        DPadRight = "BTN_DPAD_RIGHT"
        DPadUp = "BTN_DPAD_UP"
        DPadDown = "BTN_DPAD_DOWN"
        LeftGrip = "BTN_GEAR_DOWN"
        RightGrip = "BTN_GEAR_UP"

    def get_vehicle_inputs(self):
        roll_mode = self.get(SteamController.Button.LeftGrip)

        return {
            InputChannel.FORWARD: -self.get(
                SteamController.JoystickAxis.ThumbstickY) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL: self.get(SteamController.JoystickAxis.ThumbstickX) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.get(SteamController.Trigger.RightTrigger) -
                                    self.get(SteamController.Trigger.LeftTrigger)) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH: self.get(SteamController.JoystickAxis.RightPadY) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW: 0 if roll_mode else self.get(
                SteamController.JoystickAxis.RightPadX) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL: 0 if not roll_mode else self.get(
                SteamController.JoystickAxis.RightPadX) * ROTATIONAL_SENSITIVITY,
        }


class XboxController(Controller):
    def __init__(self, get_big_video_index):
        super().__init__(get_big_video_index)
        self.JOY_RANGE = (-32767, 32768)
        self.TRIG_RANGE = (0, 1024)

    class JoystickAxis(Controller.JoystickAxis):
        LeftStickX = "ABS_X"
        LeftStickY = "ABS_Y"
        RightStickX = "ABS_RX"
        RightStickY = "ABS_RY"
        DPadX = "ABS_HAT0X"
        DPadY = "ABS_HAT0Y"

    class Trigger(Controller.Trigger):
        LeftTrigger = "ABS_Z"
        RightTrigger = "ABS_RZ"

    class Button(Controller.Button):
        LeftBumper = "BTN_TL"
        RightBumper = "BTN_TR"
        A = "BTN_SOUTH"
        X = "BTN_NORTH"
        Y = "BTN_WEST"
        B = "BTN_EAST"
        LeftStick = "BTN_THUMBL"
        RightStick = "BTN_THUMBR"
        Back = "BTN_SELECT"
        Start = "BTN_START"
        Xbox = "BTN_MODE"

    def _handle_event(self, event):
        # The Xbox Dpad is special because it is an axis with range -1 to 1
        if event.code in (self.JoystickAxis.DPadX.value, self.JoystickAxis.DPadY.value):
            self.joystick_axes[self.JoystickAxis(event.code)] = event.state
            self.check_for_camera_change(event)
        else:
            super()._handle_event(event)

    def get_vehicle_inputs(self):
        roll_mode = self.get(XboxController.Button.A)

        return {
            InputChannel.FORWARD: -self.get(
                XboxController.JoystickAxis.LeftStickY) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL: 0 if roll_mode else self.get(
                XboxController.JoystickAxis.LeftStickX) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.get(XboxController.Trigger.RightTrigger) -
                                    self.get(XboxController.Trigger.LeftTrigger)) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH: self.get(XboxController.JoystickAxis.RightStickY) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW: self.get(
                XboxController.JoystickAxis.RightStickX) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL: 0 if not roll_mode else self.get(
                XboxController.JoystickAxis.LeftStickX) * ROTATIONAL_SENSITIVITY,
        }

    def check_for_camera_change(self, event):
        if event.code == self.JoystickAxis.DPadX.value and event.state != 0:
            self.call_camera_callbacks(1)
        if event.code == self.JoystickAxis.DPadY.value:
            if event.state == -1:
                self.call_camera_callbacks(0)
            elif event.state == 1:
                self.call_camera_callbacks(2)

    def check_for_relay_toggle(self, event):
        if not event.state:
            return
        if event.code == self.Button.LeftBumper.value:
            self.call_relay_callbacks(
                Relay.PVC_BACK if self.get_big_video_index() in BACKWARD_CAM_INDICES else Relay.PVC_FRONT)
        elif event.code == self.Button.RightBumper.value:
            self.call_relay_callbacks(
                Relay.CLAW_BACK if self.get_big_video_index() in BACKWARD_CAM_INDICES else Relay.CLAW_FRONT)
        elif event.code == self.Button.X.value:
            self.call_relay_callbacks(Relay.MAGNET)
        elif event.code == self.Button.Y.value:
            self.call_relay_callbacks(Relay.LIGHTS)


class PS5Controller(Controller):
    def __init__(self, get_big_video_index):
        super().__init__(get_big_video_index)
        self.JOY_RANGE = (0, 256)
        self.TRIG_RANGE = (0, 256)

    class JoystickAxis(Controller.JoystickAxis):
        LeftStickX = "ABS_X"
        LeftStickY = "ABS_Y"
        RightStickX = "ABS_RX"
        RightStickY = "ABS_RY"
        DPadX = "ABS_HAT0X"
        DPadY = "ABS_HAT0Y"

    class Trigger(Controller.Trigger):
        LeftTrigger = "ABS_Z"
        RightTrigger = "ABS_RZ"

    class Button(Controller.Button):
        X = "BTN_SOUTH"
        Triangle = "BTN_NORTH"
        Square = "BTN_WEST"
        Circle = "BTN_EAST"
        LeftBumper = "BTN_TL"
        RightBumper = "BTN_TR"
        LeftStick = "BTN_SELECT"
        RightStick = "BTN_START"
        PlayStation = "BTN_MODE"
        Microphone = "BTN_THUMBR"
        Touchpad = "BTN_THUMBL"
        Create = "BTN_TL2"
        Options = "BTN_TR2"

    def get_vehicle_inputs(self):
        roll_mode = self.get(self.Button.X)

        return {
            InputChannel.FORWARD: -self.get(
                self.JoystickAxis.LeftStickY) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL: 0 if roll_mode else self.get(
                self.JoystickAxis.LeftStickX) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.get(self.Trigger.RightTrigger) -
                                    self.get(self.Trigger.LeftTrigger)) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH: self.get(self.JoystickAxis.RightStickY) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW: self.get(
                self.JoystickAxis.RightStickX) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL: 0 if not roll_mode else self.get(
                self.JoystickAxis.LeftStickX) * ROTATIONAL_SENSITIVITY,
        }

    def _handle_event(self, event):
        # The PS Dpad is special because it is an axis with range -1 to 1
        if event.code in (self.JoystickAxis.DPadX.value, self.JoystickAxis.DPadY.value):
            self.joystick_axes[self.JoystickAxis(event.code)] = event.state
            self.check_for_camera_change(event)
        else:
            super()._handle_event(event)

    def check_for_camera_change(self, event):
        if event.code == self.JoystickAxis.DPadX.value and event.state != 0:
            self.call_camera_callbacks(1)
        if event.code == self.JoystickAxis.DPadY.value:
            if event.state == -1:
                self.call_camera_callbacks(0)
            elif event.state == 1:
                self.call_camera_callbacks(2)

    def check_for_relay_toggle(self, event):
        if not event.state:
            return
        if event.code == self.Button.LeftBumper.value:
            self.call_relay_callbacks(
                Relay.PVC_BACK if self.get_big_video_index() in BACKWARD_CAM_INDICES else Relay.PVC_FRONT)
        elif event.code == self.Button.RightBumper.value:
            self.call_relay_callbacks(
                Relay.CLAW_BACK if self.get_big_video_index() in BACKWARD_CAM_INDICES else Relay.CLAW_FRONT)
        elif event.code == self.Button.Square.value:
            self.call_relay_callbacks(Relay.MAGNET)
        elif event.code == self.Button.Triangle.value:
            self.call_relay_callbacks(Relay.LIGHTS)


def get_active_controller_type():
    if len(devices.gamepads) == 0:
        return None
    for device in devices.gamepads:
        name = device.name.lower()
        if "sony" in name:
            return PS5Controller
        if "xbox" in name or "x-box" in name or "microsoft" in name:
            return XboxController
        if "steam" in name:
            return SteamController


def get_active_controller(get_big_video_index):
    controller_class = get_active_controller_type()

    if controller_class is None:
        return None
    return controller_class(get_big_video_index)


if __name__ == '__main__':
    for device in devices.gamepads:
        print(device)

    controller = get_active_controller(lambda: 0)
    controller.start_monitoring()
    while True:
        #print(" ".join([f"{k}: {round(v, 1)}" for k, v in controller.joystick_axes.items()]))
        # print([b.name for b, v in controller.buttons.items() if v])
        time.sleep(0.1)
