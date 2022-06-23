import subprocess
import os
from vision.transect.measure_wreck import MeasureWreck

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread

class MeasureWreckThread(QThread):

    def __init__(self):
        super().__init__()
        self.input_image = None
        self.measurer = None

    def run(self):
        if self.input_image is None:
            self.measurer = MeasureWreck(self.quit)
        else:
            self.measurer = MeasureWreck(self.quit, self.input_image)
        self.measurer.show()
    
    def exit_window(self):
        self.measurer.close()

class MeasureWreckWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.start_button = QPushButton("Measure Wreck", self)

        self.start_button.clicked.connect(self.measure_wreck)

        self.root_layout.addWidget(self.start_button)

        self.measure_thread = MeasureWreckThread()

    def on_stitch_complete(self, img):
        self.measure_thread.input_image = img
    
    def measure_wreck(self):
        if not self.measure_thread.isRunning():
            self.measure_thread.start()
        else:
            self.measure_thread.exit_window()
            self.measure_thread.quit()