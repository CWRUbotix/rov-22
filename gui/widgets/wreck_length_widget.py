import subprocess
import os
from gui.data_classes import Frame
from vision.transect.wreck_length import WreckLength
from gui.widgets.frame_capture_vision import FrameCaptureVisionThread

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread
from logger import root_logger
from util import vision_path

logger = root_logger.getChild(__name__)

class WreckLengthThread(FrameCaptureVisionThread):

    def __init__(self, App):
        super().__init__(App)

    def update(self):
        logger.debug("Starting wreck length thread")
        mapper = WreckLength()
        mapper.show_canvas()

class WreckLengthWidget():

    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.button_name = QPushButton("Find Wreck Length", self)

        self.button_name.clicked.connect(self.wreck_length)

        self.root_layout.addWidget(self.button_name)

        self.length_thread = WreckLengthThread()
    
    def wreck_length(self):
        if not self.length_thread.isRunning():
            self.length_thread.start()