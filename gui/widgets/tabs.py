import logging

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

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

    def __init__(self, num_video_streams):
        super().__init__()

        self.horizontal_layout = QHBoxLayout()
        self.root_layout.addLayout(self.horizontal_layout, 100)

        self.video_area = VideoArea(num_video_streams)
        self.horizontal_layout.addWidget(self.video_area)

        self.right_button_panel = QVBoxLayout()
        self.right_button_panel.addWidget(QPushButton("Example button right"))
        self.horizontal_layout.addLayout(self.right_button_panel)

        # Create a text label
        self.textLabel = QLabel('Webcam')

        self.bottom_button_panel = QVBoxLayout()
        self.bottom_button_panel.addWidget(self.textLabel)

        self.root_layout.addLayout(self.bottom_button_panel, 10)

    def handle_frame(self, frame: Frame):
        self.video_area.handle_frame(frame)


class MainTab(VideoTab):
    def __init__(self, num_video_streams):
        super().__init__(num_video_streams)


class DebugTab(VideoTab):
    # Create file selection signal
    select_files_signal = pyqtSignal(list)

    def __init__(self, num_video_streams):
        super().__init__(num_video_streams)

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

        # Add select files button
        self.select_files_button = QPushButton(self)
        self.select_files_button.setText("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        self.root_layout.addWidget(self.select_files_button)

    def select_files(self):
        """Run the system file selection dialog and emit results, to be recieved by VideoThread"""
        filenames, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "","All Files (*)", options=QFileDialog.Options())
        if len(filenames) > 0:
            self.select_files_signal.emit(filenames[:len(self.video_area.video_widgets)])

    def handle_frame(self, frame: Frame):
        # TODO: This should probably me replaced when VideoWidget is implemented

        # Apply the selected filter from the dropdown
        if frame.cam_index == self.video_area.get_big_video_cam_index():
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