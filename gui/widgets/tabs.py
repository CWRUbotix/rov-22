import logging

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget, QTextEdit

from gui.widgets.video_controls_widget import VideoControlsWidget
from gui.widgets.video_widgets import VideoArea
from gui.data_classes import Frame
from gui.decorated_functions import dropdown


CONSOLE_TEXT_COLORS = {
    logging.DEBUG: QColor.fromRgb(0xffffff),
    logging.INFO: QColor.fromRgb(0xffffff),
    logging.WARN: QColor.fromRgb(0xffff4f),
    logging.ERROR: QColor.fromRgb(0xff4f4f),
    logging.CRITICAL: QColor.fromRgb(0xff4f4f)
}


class RootTab(QWidget):
    """An individual tab in the RootTabContainer containing all the widgets to be displayed in the tab"""

    def __init__(self):
        super().__init__()

        # Create a new vbox layout to contain the tab's widgets
        self.root_layout = QVBoxLayout(self)
        self.setLayout(self.root_layout)

        text_label = QLabel()
        text_label.setText("Console")
        self.root_layout.addWidget(text_label)

        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setLineWrapMode(QTextEdit.NoWrap)

        font = self.console.font()
        font.setFamily("Courier")
        font.setPointSize(12)

        self.root_layout.addWidget(self.console)

    @pyqtSlot(str, int)
    def update_console(self, line: str, severity: int):
        self.console.moveCursor(QTextCursor.End)
        self.console.setTextColor(CONSOLE_TEXT_COLORS[severity])

        self.console.insertPlainText(line)

        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class VideoTab(RootTab):
    """A RootTab which displays video(s) from a camera stream or video file, among other functions"""

    def __init__(self):
        super().__init__()

        # TODO: Replace with an instance of VideoArea and several VideoWidgets
        # Create the labels that hold the images
        self.image_labels = []
        for i in range(0, 2):
            label = QLabel(self)
            self.image_labels.append(label)
            self.root_layout.insertWidget(i, label)

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

        self.current_filter = "None"  # Filter applied with dropdown menu

        # Creating combo_box and adding the functions
        self.combo_box = QComboBox()

        for func_name in dropdown.func_dictionary.keys():
            self.combo_box.addItem(func_name)

        self.combo_box.currentTextChanged.connect(self.update_current_filter)
        self.update_current_filter(self.combo_box.currentText())

        self.root_layout.addWidget(self.combo_box)

        # Add video control buttons
        self.video_controls = VideoControlsWidget()
        self.root_layout.addWidget(self.video_controls)

    def handle_frame(self, frame: Frame):
        # TODO: This should probably me replaced when VideoWidget is implemented

        # Apply the selected filter from the dropdown
        if frame.cam_index == 0:
            frame.cv_img = self.apply_filter(frame.cv_img)

        super().handle_frame(frame)

    def update_current_filter(self, text):
        """
        Calls the function selected in the dropdown menu
        :param text: Name of the function to call
        """

        self.current_filter = text

    def apply_filter(self, frame):
        """
        Applies filter from the dropdown menu to the given frame
        :param frame: frame to apply filter to
        :return: frame with filter applied
        """
        return dropdown.func_dictionary.get(self.current_filter)(frame)
