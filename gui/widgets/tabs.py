
import logging
import os
from types import SimpleNamespace

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QTextCursor, QFont
from PyQt5.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QFrame
import cv2

from gui.widgets.vehicle_status_widget import VehicleStatusWidget
from gui.widgets.image_debug_widget import ImagesWidget
from gui.widgets.video_controls_widget import VideoControlsWidget
from gui.widgets.video_widgets import VideoArea
from gui.widgets.fish_widget import FishRecordWidget
from gui.data_classes import Frame, VideoSource
from gui.widgets.arm_control_widget import ArmControlWidget
from gui.decorated_functions import dropdown

# Temporary imports for basic image debug tab
import os
from util import data_path

CONSOLE_TEXT_COLORS = {
    logging.DEBUG: QColor.fromRgb(0xffffff),
    logging.INFO: QColor.fromRgb(0xffffff),
    logging.WARN: QColor.fromRgb(0xffff4f),
    logging.ERROR: QColor.fromRgb(0xff4f4f),
    logging.CRITICAL: QColor.fromRgb(0xff4f4f)
}

HEADER_FONT = QFont("Sans Serif", 12)


class RootTab(QWidget):
    """An individual tab in the RootTabContainer containing all the widgets to be displayed in the tab"""

    def __init__(self):
        super().__init__()

        self.widgets = SimpleNamespace()  # An empty object which will contain all the widgets in the tab
        self.layouts = SimpleNamespace()  # An empty object which will contain all the layouts in the tab

        self.init_widgets()
        self.organize()

    def init_widgets(self):
        console = QTextEdit(self)
        console.setReadOnly(True)

        console_font = console.font()
        console_font.setFamily("Courier")
        console_font.setPointSize(12)

        self.widgets.console = console

    def organize(self):
        """
        Create layouts and widgets to organize the widgets in self.widgets into a coherent gui
        """

        # Create a new hbox layout to contain the tab's widgets
        root_layout = QHBoxLayout(self)
        self.setLayout(root_layout)
        self.layouts.root_layout = root_layout

        main_vbox = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar = QVBoxLayout()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFrameShape(QFrame.Box)

        root_layout.addLayout(main_vbox, 3)
        root_layout.addWidget(sidebar_frame, 1)

        self.layouts.main_vbox = main_vbox
        self.layouts.sidebar = sidebar

    @pyqtSlot(str, int)
    def update_console(self, line: str, severity: int):
        self.widgets.console.moveCursor(QTextCursor.End)
        self.widgets.console.setTextColor(CONSOLE_TEXT_COLORS[severity])

        self.widgets.console.insertPlainText(line + "\n")

        scrollbar = self.widgets.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class ImageDebugTab(RootTab):
    """A RootTab which displays and filters image(s)"""

    def init_widgets(self):
        self.widgets.images_widget = ImagesWidget()
        self.widgets.images_widget.show()
        self.widgets.images_widget.set_folder(os.path.join(data_path, 'example-images', 'star'))

    def organize(self):
        super().organize()
        self.layouts.main_vbox.addWidget(self.widgets.images_widget)


class VideoTab(RootTab):
    """A RootTab which displays video(s) from a camera stream or video file, among other functions"""

    def __init__(self, num_video_streams):
        self.num_video_streams = num_video_streams

        super().__init__()

    def init_widgets(self):
        super().init_widgets()
        self.widgets.video_area = VideoArea(self.num_video_streams)

    def handle_frame(self, frame: Frame):
        self.widgets.video_area.handle_frame(frame)

    def organize(self):
        super().organize()

        self.layouts.main_vbox.addWidget(self.widgets.video_area, 7)

        text_label = QLabel()
        text_label.setText("Console")
        self.layouts.main_vbox.addWidget(text_label)
        self.layouts.main_vbox.addWidget(self.widgets.console, 1)


def header_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setFont(HEADER_FONT)
    label.setAlignment(QtCore.Qt.AlignCenter)
    return label


class MainTab(VideoTab):
    def __init__(self, app, num_video_streams):
        self.app = app
        super().__init__(num_video_streams)
        

    def init_widgets(self):
        super().init_widgets()
        self.widgets.fish_record = FishRecordWidget(self.app.video_thread)
        self.widgets.arm_control = ArmControlWidget()
        self.widgets.vehicle_status = VehicleStatusWidget()

    def organize(self):
        super().organize()
        self.layouts.sidebar.addWidget(self.widgets.fish_record)
        self.layouts.sidebar.addStretch()
        self.layouts.sidebar.addWidget(self.widgets.arm_control)
        self.layouts.sidebar.addWidget(self.widgets.vehicle_status)


class DebugTab(VideoTab):
    # Create file selection signal
    select_files_signal = pyqtSignal(list)

    def __init__(self, num_video_streams):
        self.current_filter = "None"  # Filter applied with dropdown menu

        super().__init__(num_video_streams)

    def init_widgets(self):
        super().init_widgets()

        # Creating combo_box and adding the functions
        combo_box = QComboBox()

        for func_name in dropdown.func_dictionary.keys():
            combo_box.addItem(func_name)

        combo_box.currentTextChanged.connect(self.update_current_filter)
        self.update_current_filter(combo_box.currentText())

        self.widgets.filter_dropdown = combo_box

        # Add video control buttons
        video_controls = VideoControlsWidget()
        self.widgets.video_controls = video_controls

        # Add select files button
        select_files_button = QPushButton(self)
        select_files_button.setText("Select Files")
        select_files_button.clicked.connect(self.select_files)
        self.widgets.select_files_button = select_files_button

    def organize(self):
        super().organize()

        sidebar = self.layouts.sidebar

        sidebar.addWidget(header_label("Filter"))
        sidebar.addWidget(self.widgets.filter_dropdown)

        sidebar.addWidget(header_label("Video Controls"))
        sidebar.addWidget(self.widgets.video_controls)

        sidebar.addWidget(self.widgets.select_files_button)
        sidebar.addStretch()

    def select_files(self):
        """Run the system file selection dialog and emit results, to be recieved by VideoThread"""
        filenames, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "Video/Config (*.mp4 *.json)",
                                                    options=QFileDialog.Options())
        
        if len(filenames) != 0:
            self.select_files_signal.emit(filenames)

    def handle_frame(self, frame: Frame):
        # Apply the selected filter from the dropdown
        if frame.cam_index == self.widgets.video_area.get_big_video_cam_index():
            frame.cv_img = self.apply_filter(frame.cv_img)

        super().handle_frame(frame)

    def update_current_filter(self, text):
        """
        Calls the function selected in the dropdown menu
        :param text: Name of the function to call
        """

        self.current_filter = text

    def apply_filter(self, frame: Frame):
        """
        Applies filter from the dropdown menu to the given frame
        :param frame: frame to apply filter to
        :return: frame with filter applied
        """
        return dropdown.func_dictionary.get(self.current_filter)(frame)
