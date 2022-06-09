from gui.data_classes import Frame
from gui.video_thread import VideoThread
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot


ARM_STYLE = "QPushButton { background-color: green }"
DISARM_STYLE = "QPushButton { background-color: red }"
DISABLED_STYLE = "QPushButton { background-color: #575757 }"


class FishRecordWidget(QWidget):
    counter = 0

    def __init__(self, video_thread: VideoThread):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.record_button = QPushButton('Record Fish', self)
        self.record_button.clicked.connect(self.on_record_button)
        
        self.recording = False
        self.video_thread = video_thread

        self.root_layout.addWidget(self.record_button)
        #self.video_thread.update_frames_signal.connect(self.handle_frame)
    
    def on_record_button(self):
        if self.recording:
            self.video_thread.update_frames_signal.disconnect(self.handle_frame)
        else:
            self.video_thread.update_frames_signal.connect(self.handle_frame)
        
        self.recording = not self.recording
    
    @pyqtSlot(Frame)
    def handle_frame(self):
        print('test')