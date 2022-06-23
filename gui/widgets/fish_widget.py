import math
from multiprocessing import Process, Queue, RawArray, Array
from multiprocessing.shared_memory import SharedMemory

import numpy as np
from vision.stereo.stereo_util import StereoCoordinate, draw_crosshairs
from vision.stereo.params import StereoParameters
from vision.stereo.pixels import PixelSelector, QPixelWidget
from gui.gui_util import convert_cv_qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot
import cv2

from logger import root_logger

logger = root_logger.getChild(__name__)


class FishRecordWidget(QWidget):
    pictures = ([], [], [])

    def __init__(self, app):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.capture_button = QPushButton('Capture Fish 1', self)
        self.capture_button.clicked.connect(lambda: self.on_capture(0))
        self.root_layout.addWidget(self.capture_button)

        self.capture_button2 = QPushButton('Capture Fish 2', self)
        self.capture_button2.clicked.connect(lambda: self.on_capture(1))
        self.root_layout.addWidget(self.capture_button2)

        self.capture_button3 = QPushButton('Capture Fish 3', self)
        self.capture_button3.clicked.connect(lambda: self.on_capture(2))
        self.root_layout.addWidget(self.capture_button3)

        calculate_button = QPushButton('Calculate Lengths', self)
        calculate_button.clicked.connect(self.on_calculate)
        self.root_layout.addWidget(calculate_button)

        self.app = app

        # self.video_thread.update_frames_signal.connect(self.handle_frame)

    def on_capture(self, idx: int):
        logger.info(f'Captured fish {idx}')
        self.pictures[idx].append(self.app.get_active_frame().copy())

    def on_calculate(self):
        self.widget = FishMeasurementWindow(self.pictures)
        self.widget.show()


class FishMeasurementWindow(QWidget):

    def __init__(self, imgs) -> None:
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.measurement_widget = FishMeasurmentWidget(imgs)
        layout.addWidget(self.measurement_widget)

        meausre_button = QPushButton('Measure')
        meausre_button.clicked.connect(self.on_measure)
        layout.addWidget(meausre_button)

    def on_measure(self):
        self.measurement_widget.measure()


class FishMeasurmentWidget(QScrollArea):
    def __init__(self, imgs):
        super().__init__()
        # self.setGeometry(0, 0, 1920, 1080)
        self.setGeometry(600, 100, 1000, 900)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)

        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        self.setWidget(widget)

        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

        self.capture_widgets = ([], [], [])

        for i in range(3):
            col_layout = QVBoxLayout()

            for img in imgs[i]:
                img_widget = FishCaptureWidget(img, self.thread_pool)
                col_layout.addWidget(img_widget)
                self.capture_widgets[i].append(img_widget)
            
            col_layout.addStretch()
            
            layout.addLayout(col_layout)

        self.pictures = imgs

    def measure(self):
        fish_sum = 0
        for i in range(3):
            sum = 0
            count = 0
            logger.info(f'Fish {i + 1} measurmenets:')
            for widget in self.capture_widgets[i]:
                dist = widget.distance()
                if dist is not None:
                    logger.info(dist)
                    sum += dist
                    count += 1
            avg = sum / count
            fish_sum += avg
            logger.info(f'Fish {i + 1} average: {avg}')

        logger.info(f'Average of all fish: {fish_sum / 3}')

        
def run_selector(arr_l: SharedMemory, arr_r: SharedMemory, shape_l, shape_r, queue: Queue):
    print('RUNNING SELECTOR')
    img_l = np.frombuffer(arr_l.buf, dtype=np.uint8).reshape(shape_l).copy()
    print(f'Image: {img_l.sum()}')
    img_r = np.frombuffer(arr_r.buf, dtype=np.uint8).reshape(shape_r).copy()
    selector = PixelSelector(img_l, img_r, StereoParameters.load('stereo-pool'))
    coord = selector.run()
    queue.put(coord)


class FishCaptureWidget(QLabel):
    coord_slot = pyqtSlot(object)
    measuring = False

    def __init__(self, img, thread_pool: QThreadPool):
        super().__init__()
        self.orig_img = cv2.resize(img, (1280, 480))
        
        self.setMinimumSize(400, 400)
        self.thread_pool = thread_pool

        self.coord1 = None
        self.coord2 = None
        self.params = StereoParameters.load('stereo-pool')
        self.img = self.params.rectify_stereo(cv2.resize(img, (1280, 480)))
        self.setPixmap(convert_cv_qt(self.img, width=480, height=800))
    
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if not self.measuring:
            self.sel = QPixelWidget(self.orig_img[:, 0:640], self.orig_img[:, 640:1280],
                                    StereoParameters.load('stereo-pool'))
            self.sel.measurement_widget.coord_signal.connect(self.on_coord)
            self.sel.show()
    
    @pyqtSlot(object)
    def on_coord(self, coord: StereoCoordinate):
        if not self.measuring:
            self.coord1 = coord
            if coord is not None:
                self.measuring = True
                self.sel = QPixelWidget(self.orig_img[:, 0:640], self.orig_img[:, 640:1280],
                                        StereoParameters.load('stereo-pool'))
                self.sel.measurement_widget.coord_signal.connect(self.on_coord)
                self.sel.show()
            else:
                self._clear_coords()
        else:
            self.coord2 = coord
            self.measuring = False
            if coord is not None:
                img_annotated = draw_crosshairs(self.img, self.coord1.xl, self.coord1.y, thickness=5)
                img_annotated = draw_crosshairs(img_annotated, self.coord1.xr + 640, self.coord1.y, thickness=5)
                img_annotated = draw_crosshairs(img_annotated, self.coord2.xl, self.coord2.y, color=(0, 120, 255), thickness=5)
                img_annotated = draw_crosshairs(img_annotated, self.coord2.xr + 640, self.coord2.y, color=(0, 120, 255), thickness=5)
                self.setPixmap(convert_cv_qt(img_annotated, width=480, height=800))
            else:
                self._clear_coords()

    def _clear_coords(self):
        self.coord1 = None
        self.coord2 = None
        self.setPixmap(convert_cv_qt(self.img, width=480, height=800))

    def distance(self):
        if self.coord1 is not None and self.coord2 is not None:
            point1 = self.params.triangulate_stereo_coord(self.coord1)
            point2 = self.params.triangulate_stereo_coord(self.coord2)
            dist = math.dist(point1, point2) * 2.126447913752668
            return dist
        else:
            return None
