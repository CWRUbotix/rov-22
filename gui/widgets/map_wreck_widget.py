import subprocess
import os

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from logger import root_logger
from util import vision_path

logger = root_logger.getChild(__name__)
script_path = os.path.join(vision_path, "vision", "transect", "map_wreck.py") 

def map_wreck():
    logger.debug("Opening map wreck window")

    subprocess.Popen(["python", script_path])

class MapWreckWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.pause_button = QPushButton("Map Wreck", self)

        self.pause_button.clicked.connect(map_wreck)

        self.root_layout.addWidget(self.pause_button)