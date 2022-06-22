from vision.transect.stitch_manual import stitch_manually
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QThread
from logger import root_logger

logger = root_logger.getChild(__name__)

class CaptureThread(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        logger.info("")
        
class StitchManualThread(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        logger.info("Starting manual transect stitching")
        stitch_manually()

class TransectWidget(QWidget):
    def __init__(self, app):
        super().__init__()

        self.app = app

        # Horizontal layout
        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        # Creating the buttons
        self.capture_button = QPushButton("Capture Transect", self)
        self.capture_button.clicked.connect(self.capture)

        self.manual_button = QPushButton("Stitch Manually", self)
        self.manual_button.clicked.connect(self.stitch_manually)     

        self.root_layout.addWidget(self.capture_button)
        self.root_layout.addWidget(self.manual_button)

        self.capture_thread = CaptureThread()
        self.manual_stitch_thread = StitchManualThread()

    def capture(self):
        if not self.capture_thread.isRunning():
            self.capture_thread.start()

    def stitch_manually(self):
        if not self.manual_stitch_thread.isRunning():
            self.manual_stitch_thread.start()