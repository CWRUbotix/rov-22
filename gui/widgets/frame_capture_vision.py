import subprocess
import os
from unicodedata import name


from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QThread
from gui.data_classes import Frame
from logger import root_logger
from util import vision_path

logger = root_logger.getChild(__name__)

class FrameCaptureVisionThread(QThread):

    def __init__(self, App):
        super().__init__(App)
        self.chosen_frame_list = []
        self.frame_list = App.frame_list
        self.cam_index = App.cam_index
        
    def run(self):
        self.setFrame()
        self.update(self.frame_List)

    def setFrame(self):
        self.chosen_frame_list.append(self.Frame_list[self.cam_index])

    #def update(self):
        

class FrameCaptureVisionWidget(QWidget):

    def __init__(self, App):
        super().__init__(App)

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.button_name = QPushButton("Capture Frame", self)

        self.button_name.clicked.connect(self.widget_update)

        self.root_layout.addWidget(self.button_name)

        self.length_thread = FrameCaptureVisionThread(App)
    
    def widget_update(self):
        if not self.length_thread.isRunning():
            self.length_thread.start()