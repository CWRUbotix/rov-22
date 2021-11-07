import dataclasses
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread


@dataclasses.dataclass
class Frame:
    cv_img: np.ndarray
    cam_index: int


def convert_cv_qt(cv_img):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    return QPixmap.fromImage(convert_to_qt_format)


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


class RootTab(QWidget):
    """An individual tab in the RootTabContainer containing all the widgets to be displayed in the tab"""

    def __init__(self):
        super().__init__()

        # Create a new vbox layout to contain the tab's widgets
        self.root_layout = QVBoxLayout(self)
        self.setLayout(self.root_layout)


class VideoTab(RootTab):
    """A RootTab which displays video(s) from a camera stream or video file, among other functions"""

    def __init__(self):
        super().__init__()

        # TODO: Replace with an instance of VideoArea and several VideoWidgets
        # Create the labels that hold the images
        self.image_labels = []
        for i in range(0, 2):
            self.image_labels.append(QLabel(self))

        # Add the image labels to the tab
        for label in self.image_labels:
            self.root_layout.addWidget(label)

    def handle_frame(self, frame: Frame):
        qt_img = convert_cv_qt(frame.cv_img)

        # Scale image
        # TODO: VideoWidget should handle the scaling
        scaled_img = qt_img.scaled(640, 480, Qt.KeepAspectRatio)

        # Update the image label corresponding to the cam_index with the new frame
        # TODO: Delegate frame to the tab's VideoArea, which should update all its VideoWidgets with the same cam_index
        self.image_labels[frame.cam_index].setPixmap(scaled_img)


class MainTab(VideoTab):
    def __init__(self):
        super().__init__()
        # Add widgets specific to the "Main" tab here


class DebugTab(VideoTab):
    def __init__(self):
        super().__init__()
        # Add widgets specific to the "Debug" tab here


class App(QWidget):
    def __init__(self, filenames):
        super().__init__()
        self.setWindowTitle("ROV Vision")
        self.resize(1280, 720)
        self.showMaximized()

        # Create a tab widget
        self.tabs = QTabWidget()
        self.main_tab = MainTab()
        self.debug_tab = DebugTab()

        self.tabs.resize(300, 200)
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.debug_tab, "Debug")

        # Create a vbox to hold the tabs widget
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)

        # Set the root layout to this vbox
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
        """Updates the appropriate tab with a new opencv image"""

        # Update the tab which is currently being viewed only if it is a VideoTab
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, VideoTab):
            current_tab.handle_frame(frame)
