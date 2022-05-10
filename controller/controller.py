import time
import typing as t
from inputs import get_gamepad, devices
import math
import threading
from enum import Enum
if __name__ != "__main__":
    from vehicle.vehicle_control import InputChannel


TRANSLATION_SENSITIVITY = 0.1
ROTATIONAL_SENSITIVITY = 0.5


def apply_curve(value, exponential):
    value = min(max(value, -1), 1)  # clamp the joystick input from -1 to 1
    return math.copysign(abs(value) ** exponential, value)


class Controller:
    class JoystickAxis(Enum):
        pass

    class Trigger(Enum):
        pass

    class Button(Enum):
        pass

    def __init__(self, joystick_curve_exponential=2, trigger_curve_exponential=2):
        self.MAX_JOY_VAL = None
        self.MAX_TRIG_VAL = None

        self.joystick_curve_exponential = joystick_curve_exponential
        self.trigger_curve_exponential = trigger_curve_exponential

        self.joystick_axes: t.Dict[Controller.JoystickAxis, float] = {}
        self.triggers: t.Dict[Controller.Trigger, float] = {}
        self.buttons: t.Dict[Controller.Button, bool] = {}

        self.joystick_axis_codes = [axis.value for axis in self.__class__.JoystickAxis]
        self.trigger_codes = [trigger.value for trigger in self.__class__.Trigger]
        self.button_codes = [button.value for button in self.__class__.Button]

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
        if "SYN" in code:
            return
        # print(event.code, event.state)
        if code in self.joystick_axis_codes:
            self.joystick_axes[self.__class__.JoystickAxis(
                code)] = event.state / self.MAX_JOY_VAL  # normalize between -1 and 1
        elif code in self.trigger_codes:
            self.triggers[self.__class__.Trigger(code)] = event.state / self.MAX_TRIG_VAL
        elif code in self.button_codes:
            self.buttons[self.__class__.Button(code)] = bool(event.state)
        else:
            print(f"Unrecognized: {code}")

    def get(self, control: t.Union[JoystickAxis, Trigger, Button]) -> t.Union[float, bool]:
        if isinstance(control, self.__class__.JoystickAxis):
            return apply_curve(self.joystick_axes.get(control, 0), self.joystick_curve_exponential)
        if isinstance(control, self.__class__.Trigger):
            return apply_curve(self.triggers.get(control, 0), self.trigger_curve_exponential)
        if isinstance(control, self.__class__.Button):
            return self.buttons.get(control, False)

    def get_vehicle_inputs(self):
        raise Exception("Abstract method get_vehicle_inputs() was not overriden")


class SteamController(Controller):
    def __init__(self):
        super().__init__()
        self.MAX_JOY_VAL = 32768
        self.MAX_TRIG_VAL = 256

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
                SteamController.JoystickAxis.LeftPadY) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL: self.get(SteamController.JoystickAxis.LeftPadX) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.get(SteamController.Trigger.RightTrigger) -
                                    self.get(SteamController.Trigger.LeftTrigger)) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH: self.get(SteamController.JoystickAxis.RightPadY) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW: 0 if roll_mode else self.get(
                SteamController.JoystickAxis.RightPadX) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL: 0 if not roll_mode else self.get(
                SteamController.JoystickAxis.RightPadX) * ROTATIONAL_SENSITIVITY,
        }


class XboxController(Controller):
    def __init__(self):
        super().__init__()
        self.MAX_JOY_VAL = 32768
        self.MAX_TRIG_VAL = 1024

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
        if event.code in ("ABS_HAT0X", "ABS_HAT0Y"):
            self.joystick_axes[self.__class__.JoystickAxis(event.code)] = event.state
        else:
            super()._handle_event(event)

    def get_vehicle_inputs(self):
        roll_mode = self.get(XboxController.Button.LeftBumper)

        return {
            InputChannel.FORWARD: -self.get(
                XboxController.JoystickAxis.LeftStickY) * TRANSLATION_SENSITIVITY,
            InputChannel.LATERAL: self.get(XboxController.JoystickAxis.LeftStickX) * TRANSLATION_SENSITIVITY,
            InputChannel.THROTTLE: (self.get(XboxController.Trigger.RightTrigger) -
                                    self.get(XboxController.Trigger.LeftTrigger)) * TRANSLATION_SENSITIVITY,
            InputChannel.PITCH: self.get(XboxController.JoystickAxis.RightStickY) * ROTATIONAL_SENSITIVITY,
            InputChannel.YAW: 0 if roll_mode else self.get(
                XboxController.JoystickAxis.RightStickX) * ROTATIONAL_SENSITIVITY,
            InputChannel.ROLL: 0 if not roll_mode else self.get(
                XboxController.JoystickAxis.RightStickX) * ROTATIONAL_SENSITIVITY,
        }


def get_active_controller():
    if len(devices.gamepads) == 0:
        return None
    for device in devices.gamepads:
        name = device.name.lower()
        if "steam" in name:
            return SteamController()
        if "xbox" in name or "microsoft" in name:
            return XboxController()
    return None


if __name__ == '__main__':
    for device in devices.gamepads:
        print(device)

    controller = get_active_controller()
    controller.start_monitoring()
    while True:
        print(" ".join([f"{k}: {round(v, 1)}" for k, v in controller.joystick_axes.items()]))
        # print([b.name for b, v in controller.buttons.items() if v])
        time.sleep(0.1)
