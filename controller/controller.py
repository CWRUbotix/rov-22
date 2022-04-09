import time
import typing as t
from inputs import get_gamepad, devices
import math
import threading
from enum import Enum


class Controller:
    class JoystickAxis(Enum):
        pass

    class Trigger(Enum):
        pass

    class Button(Enum):
        pass

    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.joystick_axes: t.Dict[Controller.JoystickAxis, float] = {}
        self.triggers: t.Dict[Controller.Trigger, float] = {}
        self.buttons: t.Dict[Controller.Button, bool] = {}

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True

    def start_monitoring(self):
        self._monitor_thread.start()

    def _monitor_controller(self):
        joystick_axis_codes = [axis.value for axis in self.__class__.JoystickAxis]
        trigger_codes = [trigger.value for trigger in self.__class__.Trigger]
        button_codes = [button.value for button in self.__class__.Button]

        while True:
            events = get_gamepad()
            for event in events:
                if "SYN" in event.code:
                    continue
                if event.code in joystick_axis_codes:
                    self.joystick_axes[self.__class__.JoystickAxis(
                        event.code)] = event.state / self.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code in trigger_codes:
                    self.triggers[self.__class__.Trigger(event.code)] = event.state / self.MAX_TRIG_VAL
                elif event.code in button_codes:
                    self.buttons[self.__class__.Button(event.code)] = bool(event.state)
                else:
                    print(f"Unrecognized: {event.code}")
            time.sleep(0.01)

    def get(self, control: t.Union[JoystickAxis, Trigger, Button]) -> t.Union[float, bool]:
        if isinstance(control, self.__class__.JoystickAxis):
            return self.joystick_axes.get(control, 0)
        if isinstance(control, self.__class__.Trigger):
            return self.triggers.get(control, 0)
        if isinstance(control, self.__class__.Button):
            return self.buttons.get(control, False)


class SteamController(Controller):
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


class XboxController(Controller):
    class JoystickAxis(Controller.JoystickAxis):
        pass
        LeftStickX = "ABS_X"
        LeftStickY = "ABS_Y"
        # LeftPadX = "ABS_HAT0X"
        # LeftPadY = "ABS_HAT0Y"
        # RightPadX = "ABS_RX"
        # RightPadY = "ABS_RY"

    class Trigger(Controller.Trigger):
        pass
        # LeftTrigger = "ABS_HAT2Y"
        # RightTrigger = "ABS_HAT2X"

    class Button(Controller.Button):
        pass
        # LeftTrigger = "BTN_TL2"
        # RightTrigger = "BTN_TR2"
        # LeftBumper = "BTN_TL"
        # RightBumper = "BTN_TR"
        # A = "BTN_SOUTH"
        # X = "BTN_NORTH"
        # Y = "BTN_WEST"
        # B = "BTN_EAST"
        # Back = "BTN_SELECT"
        # Start = "BTN_START"
        # LeftPadTouch = "BTN_THUMB"
        # RightPadTouch = "BTN_THUMB2"
        # RightPadClick = "BTN_THUMBR"
        # RightPad = "BTN_THUMB2-"
        # DPadLeft = "BTN_DPAD_LEFT"
        # DPadRight = "BTN_DPAD_RIGHT"
        # DPadUp = "BTN_DPAD_UP"
        # DPadDown = "BTN_DPAD_DOWN"
        # LeftGrip = "BTN_GEAR_DOWN"
        # RightGrip = "BTN_GEAR_UP"


if __name__ == '__main__':
    for device in devices:
        print(device)

    controller = XboxController()
    controller.start_monitoring()
    while True:
        # print(" ".join([f"{k}: {round(v, 1)}" for k, v in controller.joystick_axes.items()]))
        # print([b.name for b, v in controller.buttons.items() if v])
        time.sleep(0.01)
