import json
import logging
from collections import defaultdict

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

from gui.data_classes import Frame
from gui.video_thread import VideoThread
from gui.widgets.tabs import MainTab, DebugTab, ImageDebugTab, VideoTab
from logger import root_logger
from tasks.no_button_docking import NoButtonDocking
from vehicle.vehicle_control import VehicleControl
from tasks.scheduler import TaskScheduler
from tasks.keyboard_control import KeyboardControl

from util import data_path

# The name of the logger will be included in debug messages, so set it to the name of the file to make the log traceable
logger = root_logger.getChild(__name__)


class GuiLogHandler(logging.Handler):
    def __init__(self, update_signal):
        super().__init__()
        self.update_signal = update_signal

    def emit(self, record):
        self.update_signal.emit(self.format(record), record.levelno)


class App(QWidget):
    main_log_signal = pyqtSignal(str, int)
    debug_log_signal = pyqtSignal(str, int)

    def __init__(self, args):
        super().__init__()
        self.setWindowTitle("ROV Vision")
        self.resize(1280, 720)

        if args.fullscreen:
            self.showFullScreen()

        if args.maximize:
            self.showMaximized()

        # Create the video capture thread
        with args.cameras as file:
            json_data = json.load(file)
        self.video_thread = VideoThread(json_data)

        # Dictionary to keep track of which keys are pressed. If a key is not in the dict, assume it is not pressed.
        self.keysDown = defaultdict(lambda: False)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.main_tab = MainTab(len(self.video_thread._video_sources))
        self.debug_tab = DebugTab(len(self.video_thread._video_sources))
        self.image_tab = ImageDebugTab()

        self.tabs.resize(300, 200)
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.debug_tab, "Debug")
        self.tabs.addTab(self.image_tab, "Images")

        # Create a vbox to hold the tabs widget
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)

        # Set the root layout to this vbox
        self.setLayout(vbox)

        # Create VehicleControl object to handle the connection to the ROV
        self.vehicle = VehicleControl(port=14550)

        # Setup the task scheduling thread
        self.task_scheduler = TaskScheduler(self.vehicle)
        self.task_scheduler.default_task = KeyboardControl(self.vehicle, self.keysDown)

        # Create the autonomous tasks
        self.no_button_docking_task = NoButtonDocking(self.vehicle)

        # Setup GUI logging
        gui_formatter = logging.Formatter("[{levelname}] {message}", style="{")

        self.main_log_handler = GuiLogHandler(self.main_log_signal)
        self.main_log_handler.setLevel(logging.INFO)
        self.main_log_handler.setFormatter(gui_formatter)
        root_logger.addHandler(self.main_log_handler)

        self.debug_log_handler = GuiLogHandler(self.debug_log_signal)
        self.debug_log_handler.setLevel(logging.DEBUG)
        self.debug_log_handler.setFormatter(gui_formatter)
        root_logger.addHandler(self.debug_log_handler)

        # Connect the disparate parts of the gui which need to communicate
        self.connect_signals()

        # Start the independent threads
        self.video_thread.start()
        self.task_scheduler.start()

        logger.debug("Application initialized")

    def connect_signals(self):
        # Connect the loggers to the console
        self.main_log_signal.connect(self.main_tab.update_console)
        self.debug_log_signal.connect(self.debug_tab.update_console)

        # Connect the video thread signal to the update_image function
        self.video_thread.update_frames_signal.connect(self.update_image)
        self.video_thread.update_frames_signal.connect(self.task_scheduler.on_frame)

        for tab in (self.main_tab, self.debug_tab):
            # Connect the arm/disarm gui buttons to the arm/disarm commands
            tab.widgets.arm_control.arm_button.clicked.connect(self.vehicle.arm)
            tab.widgets.arm_control.disarm_button.clicked.connect(self.vehicle.disarm)
            self.vehicle.connected_signal.connect(tab.widgets.arm_control.on_connect)
            self.vehicle.disconnected_signal.connect(tab.widgets.arm_control.on_disconnect)
            self.vehicle.armed_signal.connect(tab.widgets.arm_control.on_arm)
            self.vehicle.disarmed_signal.connect(tab.widgets.arm_control.on_disarm)

            # Connect the vehicle and task scheduler to the vehicle status widget
            self.vehicle.connected_signal.connect(tab.widgets.vehicle_status.on_connect)
            self.vehicle.disconnected_signal.connect(tab.widgets.vehicle_status.on_disconnect)
            self.task_scheduler.change_task_signal.connect(tab.widgets.vehicle_status.on_task_change)

        # Connect DebugTab's selecting files signal to video thread's on_select_filenames
        self.debug_tab.select_files_signal.connect(self.video_thread.on_select_filenames)

        # Setup the debug video buttons to control the thread
        self.debug_tab.widgets.video_controls.play_pause_button.clicked.connect(self.video_thread.toggle_play_pause)
        self.debug_tab.widgets.video_controls.restart_button.clicked.connect(self.video_thread.restart)
        self.debug_tab.widgets.video_controls.toggle_rewind_button.clicked.connect(self.video_thread.toggle_rewind)
        self.debug_tab.widgets.video_controls.prev_frame_button.clicked.connect(self.video_thread.prev_frame)
        self.debug_tab.widgets.video_controls.next_frame_button.clicked.connect(self.video_thread.next_frame)

        # Connect the task buttons to the task they control
        self.main_tab.widgets.task_buttons.no_button_docking.clicked.connect(
            lambda: self.task_scheduler.start_task(self.no_button_docking_task)
        )

    def keyPressEvent(self, event):
        """Sets keyboard keys to different actions"""
        self.keysDown[event.key()] = True

        if event.key() == Qt.Key_Space:
            self.video_thread.toggle_play_pause()

        elif event.key() == Qt.Key_Left:
            self.video_thread.prev_frame()

        elif event.key() == Qt.Key_Right:
            self.video_thread.next_frame()

        elif event.key() == Qt.Key_R:
            self.video_thread.restart()

        elif event.key() == Qt.Key_T:
            self.video_thread.toggle_rewind()

    def keyReleaseEvent(self, event):
        if self.keysDown[event.key()]:
            # Remove this key from the keysDown dict, reverting it to the default value (False)
            self.keysDown.pop(event.key())

    def closeEvent(self, event):
        self.video_thread.stop()
        event.accept()

    @pyqtSlot(Frame)
    def update_image(self, frame: Frame):
        """Updates the appropriate tab with a new opencv image"""

        # Update the tab which is currently being viewed only if it is a VideoTab
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, VideoTab):
            current_tab.handle_frame(frame)
