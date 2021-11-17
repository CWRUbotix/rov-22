import dataclasses
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog, QWidget, QLabel, QComboBox, QVBoxLayout, QTabWidget, QPushButton
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

from gui.video_controls_widget import VideoControlsWidget
from gui.decorated_functions import dropdown


@dataclasses.dataclass
class Frame:
    cv_img: np.ndarray
    cam_index: int


def convert_cv_qt(cv_img):
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
    return QPixmap.fromImage(convert_to_qt_format)


class VideoThread(QThread):
    update_frames_signal = pyqtSignal(Frame)

    def __init__(self, filenames):
        super().__init__()
        self._thread_running_flag = True
        self._video_playing_flag = True
        self._filenames = filenames
        self._captures = []
        self._rewind = False

    def _prepare_captures(self):
        """Initialize video capturers from self._filenames"""
        for filename in self._filenames:
            self._captures.append(cv2.VideoCapture(filename))

    def _emit_frames(self):
        """Emit next/prev frames on the pyqtSignal to be recieved by video widgets"""
        for index, capture in enumerate(self._captures):
            if self._rewind:
                prev_frame = cur_frame = capture.get(cv2.CAP_PROP_POS_FRAMES)

                if cur_frame >= 2:
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
        self._prepare_captures()

        # Run the play/pausable video
        while self._thread_running_flag:
            # Send frames if the video is playing
            if self._video_playing_flag:
                self._emit_frames()

            # Wait if playing normally, don't if rewinding b/c rewinding is slow
            if not self._rewind:
                self.msleep(int(1000 / 30))

        # Shut down capturers
        for capture in self._captures:
            capture.release()

    def next_frame(self):
        """Goes forward a frame if the video is paused"""
        if not self._video_playing_flag:
            prev_rewind_state = self._rewind
            self._rewind = False
            self._emit_frames()
            self._rewind = prev_rewind_state

    def prev_frame(self):
        """Goes back a frame if the video is paused"""
        if not self._video_playing_flag:
            prev_rewind_state = self._rewind
            self._rewind = True
            self._emit_frames()
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
    
    @pyqtSlot(list)
    def on_select_filenames(self, filenames):
        self._video_playing_flag = True
        self._filenames = filenames
        self._captures = []
        self._rewind = False
        self._prepare_captures()
        self._emit_frames()


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

        # Create a text label
        self.textLabel = QLabel('Webcam')
        self.root_layout.addWidget(self.textLabel)

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
    # Create file selection signal
    select_files_signal = pyqtSignal(list)
    
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

        # Add select files button
        self.select_files_button = QPushButton(self)
        self.select_files_button.setText("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        self.root_layout.addWidget(self.select_files_button)

    def select_files(self):
        """Run the system file selection dialog and emit results, to be recieved by VideoThread"""
        filenames, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "","All Files (*)", options=QFileDialog.Options())
        if len(filenames) > 0:
            self.select_files_signal.emit(filenames[:len(self.image_labels)])

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

        # Set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # Create the video capture thread
        self.thread = VideoThread(filenames)

        # Connect its signal to the update_image slot
        self.thread.update_frames_signal.connect(self.update_image)

        # Connect DebugTab's selecting files signal to video thread's on_select_filenames
        self.debug_tab.select_files_signal.connect(self.thread.on_select_filenames)

        # Setup the debug video buttons to control the thread
        self.debug_tab.video_controls.play_pause_button.clicked.connect(self.thread.toggle_play_pause)
        self.debug_tab.video_controls.toggle_rewind_button.clicked.connect(self.thread.toggle_rewind)
        self.debug_tab.video_controls.prev_frame_button.clicked.connect(self.thread.prev_frame)
        self.debug_tab.video_controls.next_frame_button.clicked.connect(self.thread.next_frame)

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
