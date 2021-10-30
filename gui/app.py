from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QComboBox
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np

from gui.decorated_functions import dropdown
from util import data_path

print(data_path)


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
        self.setWindowTitle("Qt live label demo")
        self.display_width = 250
        self.display_height = 250

        # Creating combo_box and adding the functions
        self.combo_box = QComboBox()
        self.combo_box.addItem("None")

        for func_name in dropdown.func_dictionary.keys():
            self.combo_box.addItem(func_name)

        # self.ui.combo_box.currentIndexChanged.connect(self.update_combo_box())
        self.combo_box.currentTextChanged.connect(self.update_combo_box)
        self.update_combo_box(self.combo_box.currentText())

        # Create the labels that hold the images
        self.image_labels = []
        for i in range(0, 2):
            self.image_labels.append(QLabel(self))
            self.image_labels[i].resize(self.display_width, self.display_height)

        # Create a text label
        self.textLabel = QLabel('Webcam')

        # Create a vertical box layout and add the labels
        vbox = QVBoxLayout()

        for label in self.image_labels:
            vbox.addWidget(label)

        vbox.addWidget(self.textLabel)
        vbox.addWidget(self.combo_box)

        # Set the vbox layout as the widgets layout
        self.setLayout(vbox)

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
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def update_combo_box(self, text):
        if text != "None":
            dropdown.func_dictionary[text]()