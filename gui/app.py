from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import cv2
import numpy as np

from video_controls_widget import VideoControlsWidget

class Frame():
    def __init__(self, cv_img, cam_index):
        self.cv_img = cv_img
        self.cam_index = cam_index


class VideoThread(QThread):
    update_frames_signal = pyqtSignal(Frame)

    def __init__(self, filenames):
        super().__init__()
        self._thread_running_flag = True
        self._video_playing_flag = True
        self._filenames = filenames
        self._captures = []
        self._rewind = False

    def _emit_frames(self):
        """Emit next/prev frames on the pyqtSignal to be recieved by video widgets"""
        for index, capture in enumerate(self._captures):
            if (self._rewind):
                prev_frame = cur_frame = capture.get(cv2.CAP_PROP_POS_FRAMES)
                
                if (cur_frame >= 2):
                    # Go back 2 frames so when we read() we'll read back 1 frame
                    prev_frame -= 2
                else:
                    # If at beginning, just read 1st frame over and over
                    prev_frame = 0

                capture.set(cv2.CAP_PROP_POS_FRAMES, prev_frame)
            
            # Read the frame
            ret, cv_img = capture.read()
            if ret:
                self.update_frames_signal.emit(Frame(cv_img, index))

    def run(self):
        # Create list of video capturers
        for filename in self._filenames:
            self._captures.append(cv2.VideoCapture(filename))

        # Run the play/pausable video 
        while self._thread_running_flag:
            # Send frames if the video is playing
            if self._video_playing_flag:
                self.__emit_frames()
            
            self.msleep(int(1000 / 30))

        # Shut down capturers
        for capture in self._captures:
            capture.release()
    
    def next_frame(self):
        """Goes forward a frame if the video is paused"""
        if not self._video_playing_flag:
            prev_rewind_state = self._rewind
            self._rewind = False
            self.__emit_frames()
            self._rewind = prev_rewind_state
    
    def prev_frame(self):
        """Goes back a frame if the video is paused"""
        if not self._video_playing_flag:
            prev_rewind_state = self._rewind
            self._rewind = True
            self.__emit_frames()
            self._rewind = prev_rewind_state

    def toggle_rewind(self):
        """Toggles the video rewind flag"""
        self._rewind = not self._rewind

    def toggle_play_pause(self):
        """Toggles the video playing flag"""
        self._video_playing_flag = not self._video_playing_flag
    
    def stop(self):
        """Sets the video playing & thread running flags to False and waits for thread to end"""
        self._video_playing_flag = False
        self._thread_running_flag = False
        self.wait()


class App(QWidget):
    def __init__(self, filenames):
        super().__init__()
        self.setWindowTitle("ROV Vision")
        self.disply_width = 640
        self.display_height = 480

        # Create a tab widget
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.debug_tab = QWidget()
        self.tabs.resize(300, 200)

        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.debug_tab, "Debug")

        # Create a new vbox layout for each tab
        self.main_layout = QVBoxLayout(self)
        self.debug_layout = QVBoxLayout(self)

        self.main_tab.setLayout(self.main_layout)
        self.debug_tab.setLayout(self.debug_layout)

        # Create a vbox to hold the tabs widget
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)

        # Set the root layout to this vbox
        self.setLayout(vbox)

        # Create the labels that hold the images
        self.image_labels = []
        for i in range(0, 2):
            self.image_labels.append(QLabel(self))
            self.image_labels[i].resize(self.disply_width, self.display_height)

        # Add the image labels to the main tab
        for label in self.image_labels:
            self.main_layout.addWidget(label)

        # Create the video capture thread
        self.thread = VideoThread(filenames)
        # Connect its signal to the update_image slot
        self.thread.update_frames_signal.connect(self.update_image)
        # Start the thread
        self.thread.start()

        # Add video control buttons
        self.video_controls = VideoControlsWidget(self.thread)
        self.main_layout.addWidget(self.video_controls)
        

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(Frame)
    def update_image(self, frame: Frame):
        """Updates the appropriate image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(frame.cv_img)
        # to be replace with a loop thru VideoWidgets & comparison of frame's cam_index to videowidget's cam_index
        self.image_labels[frame.cam_index].setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
