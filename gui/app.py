import datetime
import json
import logging
from collections import defaultdict
import cv2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

from gui.data_classes import Frame
from gui.video_thread import VideoThread
from gui.widgets.tabs import MainTab, DebugTab, ImageDebugTab, VideoTab
from logger import root_logger
from tasks.button_docking import ButtonDocking
from tasks.no_button_docking import NoButtonDocking
from vehicle.processes import LightsManager, CameraManager
from vehicle.vehicle_control import VehicleControl, Relay
from tasks.scheduler import TaskScheduler
from tasks.keyboard_control import KeyboardControl
from tasks.controller_drive import ControllerDrive
from controller.controller import get_active_controller, get_active_controller_type

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
    key_signal = pyqtSignal(Qt.Key)

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
        self.main_tab = MainTab(len(self.video_thread._video_sources), get_active_controller_type())
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

        self.light_manager = LightsManager(self.vehicle)
        self.camera_manager = CameraManager(self.vehicle)

        # Create an instance of controller
        self.controller = get_active_controller(self.main_tab.widgets.video_area.get_big_video_cam_index)
        if self.controller is not None:
            self.controller.start_monitoring()

        # Setup the task scheduling thread
        self.task_scheduler = TaskScheduler(self.vehicle)
        if self.controller is not None:
            self.task_scheduler.default_task = ControllerDrive(self.vehicle, self.controller, self.get_big_video_index)
        else:
            self.task_scheduler.default_task = KeyboardControl(self.vehicle, self.keysDown, self.get_big_video_index)

        # Create the autonomous tasks
        self.no_button_docking_task = NoButtonDocking(self.vehicle)
        self.button_docking_task = ButtonDocking(self.vehicle)

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

            # Register the change big video method with the controller
            if self.controller is not None:
                self.controller.register_camera_callback(tab.widgets.video_area.set_as_big_video)

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
        self.main_tab.widgets.task_buttons.button_docking.clicked.connect(
            lambda: self.task_scheduler.start_task(self.button_docking_task)
        )

        # Connect the main video area big cam changed signal to the manipulator control prompts
        self.main_tab.widgets.video_area.big_video_changed_signal.connect(self.main_tab.show_prompts_for_cam)

        # Update the cameras and lights when the big video changes
        self.main_tab.widgets.video_area.big_video_changed_signal.connect(self.light_manager.handle_active_cam_change)
        self.main_tab.widgets.video_area.big_video_changed_signal.connect(self.camera_manager.handle_active_cam_change)

        # When camera state changes, update camera toggle buttons to match
        self.vehicle.cameras_set_signal.connect(self.main_tab.widgets.camera_toggle.on_cameras_update)

        # Connect relay buttons to relays
        for relay_button in (
            self.main_tab.widgets.front_deployer_button,
            self.main_tab.widgets.front_claw_button,
            self.main_tab.widgets.back_deployer_button,
            self.main_tab.widgets.back_claw_button,
            self.main_tab.widgets.magnet_button,
            self.main_tab.widgets.lights_button,
        ):
            self.vehicle.armed_signal.connect(relay_button.enable_click)
            self.vehicle.disarmed_signal.connect(relay_button.on_disarm)
            self.vehicle.disconnected_signal.connect(relay_button.on_disarm)

        # Connect the camera toggle widget to the cameras
        self.main_tab.widgets.camera_toggle.set_cam_signal.connect(self.vehicle.set_camera_enabled)
        self.vehicle.connected_signal.connect(self.vehicle.send_camera_state)

        # Connect the manipulator buttons to their manipulators
        self.main_tab.widgets.front_deployer_button.state_change_signal.connect(
            lambda state: self.vehicle.set_relay(Relay.PVC_FRONT, state))
        self.main_tab.widgets.front_claw_button.state_change_signal.connect(
            lambda state: self.vehicle.set_relay(Relay.CLAW_FRONT, state))
        self.main_tab.widgets.back_deployer_button.state_change_signal.connect(
            lambda state: self.vehicle.set_relay(Relay.PVC_BACK, state))
        self.main_tab.widgets.back_claw_button.state_change_signal.connect(
            lambda state: self.vehicle.set_relay(Relay.CLAW_BACK, state))
        self.main_tab.widgets.magnet_button.state_change_signal.connect(
            lambda state: self.vehicle.set_relay(Relay.MAGNET, state))
        self.main_tab.widgets.lights_button.state_change_signal.connect(self.light_manager.toggle_global_enabled)

        if self.controller is not None:
            self.controller.register_relay_callback(Relay.PVC_FRONT, self.main_tab.widgets.front_deployer_button.toggle)
            self.controller.register_relay_callback(Relay.CLAW_FRONT, self.main_tab.widgets.front_claw_button.toggle)
            self.controller.register_relay_callback(Relay.PVC_BACK, self.main_tab.widgets.back_deployer_button.toggle)
            self.controller.register_relay_callback(Relay.CLAW_BACK, self.main_tab.widgets.back_claw_button.toggle)
            self.controller.register_relay_callback(Relay.MAGNET, self.main_tab.widgets.magnet_button.toggle)
            self.controller.register_relay_callback(Relay.LIGHTS_FRONT, self.main_tab.widgets.lights_button.toggle)
        
        self.vehicle.mode_signal.connect(self.main_tab.widgets.manual_button.on_mode)
        self.main_tab.widgets.manual_button.set_mode_signal(self.vehicle.set_mode_signal)
        self.vehicle.mode_signal.connect(self.main_tab.widgets.stabilize_button.on_mode)
        self.main_tab.widgets.stabilize_button.set_mode_signal(self.vehicle.set_mode_signal)
        self.vehicle.mode_signal.connect(self.main_tab.widgets.depth_hold_button.on_mode)
        self.main_tab.widgets.depth_hold_button.set_mode_signal(self.vehicle.set_mode_signal)

        self.key_signal.connect(self.main_tab.widgets.map_wreck.map_thread.key_slot)

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
        
        elif event.key() == Qt.Key_C:
            self.capture_image()
        
        self.key_signal.emit(event.key())

    def keyReleaseEvent(self, event):
        if self.keysDown[event.key()]:
            # Remove this key from the keysDown dict, reverting it to the default value (False)
            self.keysDown.pop(event.key())

    def closeEvent(self, event):
        self.video_thread.stop()
        event.accept()

    def get_big_video_index(self):
        tab = self.tabs.currentWidget()
        if isinstance(tab, VideoTab):
            return tab.widgets.video_area.get_big_video_cam_index()
        else:
            return None
    
    def get_active_frame(self):
        return self.video_thread._cur_frames[self.get_big_video_index()]
    
    def capture_image(self):
        filename = datetime.datetime.now().strftime("recordings/%Y-%m-%d_%H%M%S") + '.png'
        cv2.imwrite(filename, self.get_active_frame())

    @pyqtSlot(Frame)
    def update_image(self, frame: Frame):
        """Updates the appropriate tab with a new opencv image"""

        # Update the tab which is currently being viewed only if it is a VideoTab
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, VideoTab):
            current_tab.handle_frame(frame)
