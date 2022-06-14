import json
import socket
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThreadPool

from gui.data_classes import CameraType

from logger import root_logger

logger = root_logger.getChild(__name__)


ARM_STYLE = "QPushButton { background-color: green }"
DISARM_STYLE = "QPushButton { background-color: red }"
DISABLED_STYLE = "QPushButton { background-color: #575757 }"


class CameraToggleWidget(QWidget):
    def __init__(self):
        super().__init__()
        socket.socket
        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self._state = {}
        self._buttons = {}
        self._thread_manager = QThreadPool()
        

        for type in CameraType:
            camera = type.value

            self._state[type.value] = False
            button = QPushButton(type.value, self)
            button.clicked.connect(self._gen_slot(camera))
            self.root_layout.addWidget(button)
            self._buttons[type.value] = button
    
    def _gen_slot(self, camera: str):
        return lambda : self._thread_manager.start(lambda :self._toggle(camera))

    def _toggle(self, camera: str):
        #return
        self._state[camera] = not self._state[camera]

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(('192.168.2.2', 5000))
                sock.sendall(bytes(json.dumps(self._state) + '\n', 'utf-8'))
            except Exception as e:
                logger.info(f'Exception in camera socket: {e}')