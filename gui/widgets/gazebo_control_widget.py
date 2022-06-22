import subprocess

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from logger import root_logger

logger = root_logger.getChild(__name__)


def pause():
    logger.debug("Pausing simulation")
    subprocess.Popen(["gz", "world", "--pause", "1"])


def unpause():
    logger.debug("Unpausing simulation")
    subprocess.Popen(["gz", "world", "--pause", "0"])


def reset():
    logger.debug("Resetting simulation")
    subprocess.Popen(["gz", "world", "--reset-models"])


class GazeboControlWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.pause_button = QPushButton("Pause", self)
        self.unpause_button = QPushButton("Unpause", self)
        self.reset_button = QPushButton("Reset", self)

        self.pause_button.clicked.connect(pause)
        self.unpause_button.clicked.connect(unpause)
        self.reset_button.clicked.connect(reset)

        self.root_layout.addWidget(self.pause_button)
        self.root_layout.addWidget(self.unpause_button)
        self.root_layout.addWidget(self.reset_button)

