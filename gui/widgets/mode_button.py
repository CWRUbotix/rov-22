from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QLabel
from PyQt5.QtCore import pyqtSlot

from logger import root_logger

logger = root_logger.getChild(__name__)

class ModeButton(QPushButton):

    def __init__(self, text, mode, parent=None, control_prompt_image=None):
        super().__init__(text, parent)
        self.mode = mode

        self.clicked.connect(self.on_click)

        self.control_prompt = QLabel()
        self.control_prompt.setFixedHeight(80)
        if control_prompt_image is not None:
            self.control_prompt.setPixmap(control_prompt_image)
    
    def set_mode_signal(self, signal: pyqtSignal):
        self.signal = signal
        
    @pyqtSlot(str)
    def on_mode(self, mode: str):
        if mode == self.mode:
            self.setStyleSheet("QPushButton { background-color: blue }")
        else:
            self.setStyleSheet("QPushButton { background-color: #DFDFDF }")
    
    def on_click(self):
        logger.info(f'CLICKED: {self.mode}')
        self.signal.emit(self.mode)
