import time

from vehicle_control import VehicleControl, InputChannel

if __name__ == "__main__":
    control_link = VehicleControl(port=14550)

    print("Waiting to connect")
    while not control_link.is_connected():
        control_link.update()
        time.sleep(0.1)
    print("Connected")

    # Arm
    control_link.arm()

    # wait until arming confirmed (can manually check with master.motors_armed())
    print("Waiting for the vehicle to arm")
    while not control_link.is_armed():
        control_link.update()
        time.sleep(0.1)
    print('Armed!')

    while True:
        control_link.update()
        control_link.set_rc_inputs({
            InputChannel.YAW: 1,
        })
        time.sleep(0.1)
