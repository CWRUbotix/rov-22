from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QTabWidget
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np


class Frame():
    def __init__(self, cv_img, cam_index):
        self.cv_img = cv_img
        self.cam_index = cam_index


class VideoThread(QThread):
    update_frames_signal = pyqtSignal(Frame)

    def __init__(self, filenames):
        super().__init__()
        self._run_flag = True
        self._filenames = filenames
        self._captures = []

    def run(self):
        # Create list of video capturers
        for filename in self._filenames:
            self._captures.append(cv2.VideoCapture(filename))

        # Emit Frames of the captures
        while self._run_flag:
            for index, capture in enumerate(self._captures):
                ret, cv_img = capture.read()
                if ret:
                    self.update_frames_signal.emit(Frame(cv_img, index))
            self.msleep(int(1000 / 30))

        # Shut down capturers
        for capture in self._captures:
            capture.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
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
