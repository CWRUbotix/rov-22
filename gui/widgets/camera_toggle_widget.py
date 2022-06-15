from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal

from vehicle.constants import Camera

from logger import root_logger

logger = root_logger.getChild(__name__)


class CameraToggleWidget(QWidget):
    set_cam_signal = pyqtSignal(Camera, bool)

    def __init__(self):
        super().__init__()
        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self._buttons = {}

        for cam in Camera:
            self._state[cam] = False
            button = QPushButton(cam.value, self)
            button.setCheckable(True)
            button.clicked.connect(lambda: self._emit(cam))
            self.root_layout.addWidget(button)
            self._buttons[cam] = button

        # Front and bottom cams start enabled
        for cam in (Camera.FRONT, Camera.BOTTOM):
            self._buttons[cam].setChecked(True)

    def _emit(self, camera: Camera):
        self.set_cam_signal.emit(camera, self._buttons[camera].isChecked())

