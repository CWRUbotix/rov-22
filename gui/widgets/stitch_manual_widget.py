from vision.transect.stitch_manual import stitch_manually
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread
from logger import root_logger

logger = root_logger.getChild(__name__)

class StitchManualThread(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        logger.info("Starting manual transect stitching thread")
        stitch_manually()

class StitchManualWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.stitch_thread = StitchManualThread()
    
    def stitch(self):
        if not self.stitch_thread.isRunning():
            self.stitch_thread.start()