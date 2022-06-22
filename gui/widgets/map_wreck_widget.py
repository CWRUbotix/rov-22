import subprocess
import os
from vision.transect.map_wreck import MapWreck

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread
from logger import root_logger
from util import vision_path

logger = root_logger.getChild(__name__)

class MapWreckThread(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        logger.debug("Starting map wreck thread")
        mapper = MapWreck()
        mapper.show_canvas()

class MapWreckWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.pause_button = QPushButton("Map Wreck", self)

        self.pause_button.clicked.connect(self.map_wreck)

        self.root_layout.addWidget(self.pause_button)

        self.map_thread = MapWreckThread()
    
    def map_wreck(self):
        if not self.map_thread.isRunning():
            self.map_thread.start()