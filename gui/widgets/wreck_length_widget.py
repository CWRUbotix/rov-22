import subprocess
import os
from vision.transect.wreck_length import WreckLength

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread
from logger import root_logger
from util import vision_path

logger = root_logger.getChild(__name__)

class WreckLengthThread(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        logger.debug("Starting wreck length thread")
        mapper = WreckLength()
        mapper.show_canvas()

class WreckLengthWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.pause_button = QPushButton("Find Wreck Length", self)

        self.pause_button.clicked.connect(self.wreck_length)

        self.root_layout.addWidget(self.pause_button)

        self.length_thread = WreckLengthThread()
    
    def wreck_length(self):
        if not self.length_thread.isRunning():
            self.length_thread.start()