from gui.gui_util import convert_cv_qt
import cv2

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from gui.data_classes import Frame


class VideoArea(QWidget):
    big_video_changed_signal = pyqtSignal(int)

    def __init__(self, num_video_widgets):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.small_videos_layout = QVBoxLayout()
        self.small_videos_layout.setContentsMargins(0, 0, 0, 0)

        big_video = VideoWidget(0, True)
        self.root_layout.addWidget(big_video, 5)

        # Create the small VideoWidgets with click events and add them to horizontal_layout
        self.video_widgets = [big_video]
        for i in range(0, num_video_widgets):
            video = VideoWidget(i, False)
            self.video_widgets.append(video)
            video.update_big_video_signal.connect(self.set_as_big_video)
            self.small_videos_layout.addWidget(video, 1)

        self.root_layout.addLayout(self.small_videos_layout, 2)
    
    def get_big_video_cam_index(self):
        """Returns the cam_index of the currently enbiggened video, for use in checking whether to apply filters"""
        return self.video_widgets[0].cam_index

    def handle_frame(self, frame: Frame):
        """Recieve a frame and assign it to the correct VideoWidget"""
        qt_img = convert_cv_qt(frame.cv_img)

        for video_widget in self.video_widgets:
            if video_widget.cam_index == frame.cam_index:
                video_widget.setPixmap(qt_img.scaled(
                    video_widget.frameGeometry().width(),
                    video_widget.frameGeometry().height(),
                    Qt.KeepAspectRatio))

    @pyqtSlot(int)
    def set_as_big_video(self, cam_index: int):
        """Swap the video with the given cam_index and the big video"""
        self.video_widgets[0].cam_index = cam_index
        self.big_video_changed_signal.emit(cam_index)


class VideoWidget(QLabel):
    update_big_video_signal = pyqtSignal(int)

    def __init__(self, cam_index: int, is_big: bool):
        super().__init__()

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.cam_index = cam_index
        self.is_big = is_big

        # Swap this video with the big video on click
        self.mousePressEvent = lambda event: self.update_big_video_signal.emit(self.cam_index)
        