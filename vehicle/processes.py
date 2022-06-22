from vehicle.constants import Relay, Camera, CAM_INDICES
from vehicle.vehicle_control import VehicleControl


class LightsManager:
    LIGHTS = [Relay.LIGHTS_FRONT, Relay.LIGHTS_BOTTOM, Relay.LIGHTS_BACK]
    CAM_INDEX_TO_LIGHT = {
        CAM_INDICES[Camera.FRONT]: Relay.LIGHTS_FRONT,
        CAM_INDICES[Camera.BOTTOM]: Relay.LIGHTS_BOTTOM,
        CAM_INDICES[Camera.DUAL]: Relay.LIGHTS_FRONT
    }

    def __init__(self, vehicle: VehicleControl):
        self.vehicle = vehicle
        self.global_enabled = False
        self.current_light = Relay.LIGHTS_FRONT

    def toggle_global_enabled(self):
        self.global_enabled = not self.global_enabled
        if self.global_enabled:
            self.update_relays()
        else:
            for light in self.LIGHTS:
                self.vehicle.set_relay(light, False)

    def handle_active_cam_change(self, index: int):
        self.current_light = self.CAM_INDEX_TO_LIGHT[index]
        self.update_relays()

    def update_relays(self):
        if self.global_enabled:
            for light in self.LIGHTS:
                self.vehicle.set_relay(light, light == self.current_light)


class CameraManager:
    ENABLED_CAMS_MAP = {
        CAM_INDICES[Camera.FRONT]: (Camera.FRONT, Camera.BOTTOM),
        CAM_INDICES[Camera.BOTTOM]: (Camera.FRONT, Camera.BOTTOM),
        CAM_INDICES[Camera.DUAL]: (Camera.DUAL, Camera.BOTTOM)
    }

    def __init__(self, vehicle: VehicleControl):
        self.vehicle = vehicle

    def handle_active_cam_change(self, index: int):
        enabled_cams = self.ENABLED_CAMS_MAP[index]
        self.vehicle.camera_states = {cam: cam in enabled_cams for cam in Camera}
        self.vehicle.send_camera_state()
