
from PyQt5.QtWidgets import QPushButton, QLabel
import os

from logger import root_logger

logger = root_logger.getChild(__name__)

class FishButton(QPushButton):

    def __init__(self, text, parent=None, control_prompt_image=None):
        super().__init__(text, parent)

        self.setFixedHeight(80)
        self.clicked.connect(self.on_click)

    def on_click(self):
        logger.info(f'CLICKED:')
        os.system("gnome-terminal -e 'bash -c \"python scripts/fish_formula.py; exec bash\"'")
