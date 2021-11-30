import cv2

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from gui.data_classes import Frame


class VideoArea(QWidget):
    def __init__(self, num_video_widgets):
        super().__init__()

        self.root_layout = QVBoxLayout(self)
        self.setLayout(self.root_layout)

        self.small_videos_layout = QHBoxLayout()
        self.small_videos_layout.setContentsMargins(0, 0, 0, 0)

        # Create VideoWidgets with click events and add them to horizontal_layout
        self.video_widgets = []
        for i in range(0, num_video_widgets):
            self.video_widgets.append(VideoWidget(i, i == 0))
            if i == 0:  # Big video
                self.root_layout.addWidget(self.video_widgets[i])
            else:       # Small videos
                self.video_widgets[i].update_big_video_signal.connect(self.set_as_big_video)
                self.small_videos_layout.addWidget(self.video_widgets[i])
        
        self.root_layout.addLayout(self.small_videos_layout)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        if len(cv_img.shape) == 2:
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
        elif len(cv_img.shape) == 3:
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError(f"cv_img must be a 2d or 3d numpy array representing an image, not {repr(cv_img)}")

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QtGui.QPixmap.fromImage(convert_to_qt_format)
    
    def get_big_video_cam_index(self):
        """Returns the cam_index of the currently enbiggened video, for use in checking whether to apply filters"""
        return self.video_widgets[0].cam_index

    def handle_frame(self, frame: Frame):
        """Recieve a frame and assign it to the correct VideoWidget"""
        qt_img = self.convert_cv_qt(frame.cv_img)

        for video_widget in self.video_widgets:
            if video_widget.cam_index == frame.cam_index:
                video_widget.setPixmap(qt_img.scaled(
                    video_widget.frameGeometry().width(),
                    video_widget.frameGeometry().height(),
                    Qt.KeepAspectRatio))

    @pyqtSlot(int)
    def set_as_big_video(self, cam_index: int):
        """Swap the video with the given cam_index and the big video"""
        for video_widget in self.video_widgets:
            if video_widget.cam_index == cam_index:
                video_widget.cam_index = self.video_widgets[0].cam_index
        
        self.video_widgets[0].cam_index = cam_index


class VideoWidget(QLabel):
    update_big_video_signal = pyqtSignal(int)

    def __init__(self, cam_index: int, is_big: bool):
        super().__init__()

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.cam_index = cam_index
        self.is_big = is_big

        # Swap this video with the big video on click
        self.mousePressEvent = lambda event: self.update_big_video_signal.emit(self.cam_index)
        