import os
import cv2

from vision.transect.stitch_manual import stitch_manually
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import QThread
from logger import root_logger
from util import data_path

logger = root_logger.getChild(__name__)

class CaptureThread(QThread):

    image_to_save = None
    image_num = 0

    def __init__(self):
        super().__init__()

    def set_image(self, image, num):
        self.image_to_save = image
        self.image_num = num

    def run(self):
        file_name = f"transect_image({self.image_num}).png"
        path = os.path.join(data_path, "transect_frames", file_name)
        cv2.imwrite(path, self.image_to_save)

        logger.info(f"Saving {file_name} to {path}")

class StitchManualThread(QThread):

    def __init__(self):
        super().__init__()

    def run(self):
        logger.info("Starting manual transect stitching")
        stitch_manually()

class TransectWidget(QWidget):
    pictures = []
    image_num = 0

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

        dir = os.path.join(data_path, "transect_frames")
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

    def capture(self):
        frame = self.app.get_active_frame()

        self.pictures.append(frame)
        self.image_num += 1

        self.capture_thread.set_image(frame, self.image_num)

        if not self.capture_thread.isRunning():
            self.capture_thread.start()

    def stitch_manually(self):
        if not self.manual_stitch_thread.isRunning():
            self.manual_stitch_thread.start()