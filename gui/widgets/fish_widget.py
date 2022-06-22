import math
from multiprocessing import Process, Queue, RawArray, Array
from multiprocessing.shared_memory import SharedMemory

import numpy as np
from vision.stereo.stereo_util import draw_crosshairs, left_half, right_half
from vision.stereo.params import StereoParameters
from vision.stereo.pixels import PixelSelector, QPixelSelector, QPixelWidget
from gui.gui_util import convert_cv_qt
from gui.data_classes import Frame
from gui.video_thread import VideoThread
from PyQt5.QtGui import QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QThreadPool, QThread
import cv2

from logger import root_logger
logger = root_logger.getChild(__name__)


class FishRecordWidget(QWidget):
    pictures = ([],[],[])

    def __init__(self, app):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        self.capture_button = QPushButton('Capture Fish 1', self)
        self.capture_button.clicked.connect(lambda : self.on_capture(0))
        self.root_layout.addWidget(self.capture_button)

        self.capture_button2 = QPushButton('Capture Fish 2', self)
        self.capture_button2.clicked.connect(lambda : self.on_capture(1))
        self.root_layout.addWidget(self.capture_button2)

        self.capture_button3 = QPushButton('Capture Fish 3', self)
        self.capture_button3.clicked.connect(lambda : self.on_capture(2))
        self.root_layout.addWidget(self.capture_button3)

        calculate_button = QPushButton('Calculate Lengths', self)
        calculate_button.clicked.connect(self.on_calculate)
        self.root_layout.addWidget(calculate_button)

        self.app = app

        
        #self.video_thread.update_frames_signal.connect(self.handle_frame)
    

    def on_capture(self, idx: int):
        print(f'Pressed {idx}')
        self.pictures[idx].append(self.app.get_active_frame())
    

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
        #self.setGeometry(0, 0, 1920, 1080)
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
            logger.info(f'Fish {i+1} measurmenets:')
            for widget in self.capture_widgets[i]:
                dist = widget.distance()
                if dist is not None:
                    logger.info(dist)
                    sum += dist
                    count += 1
            avg = sum / count
            fish_sum += avg
            logger.info(f'Fish {i+1} average: {avg}')
        
        logger.info(f'Average of all fish: {fish_sum/3}')

        
def run_selector(arr_l: SharedMemory, arr_r: SharedMemory, shape_l, shape_r, queue: Queue):
    print('RUNNING SELECTOR')
    img_l = np.frombuffer(arr_l.buf, dtype=np.uint8).reshape(shape_l).copy()
    print(f'Image: {img_l.sum()}')
    img_r = np.frombuffer(arr_r.buf, dtype=np.uint8).reshape(shape_r).copy()
    selector = PixelSelector(img_l, img_r, StereoParameters.load('stereo-pool'))
    coord = selector.run()
    queue.put(coord)


class FishCaptureWidget(QLabel):

    def __init__(self, img, thread_pool: QThreadPool):
        super().__init__()
        self.img = cv2.resize(img, (1280, 480))
        
        self.setMinimumSize(400, 400)
        self.thread_pool = thread_pool

        self.coord1 = None
        self.coord2 = None
        self.params = StereoParameters.load('stereo-pool')
        self.img = self.params.rectify_stereo(cv2.resize(img, (1280, 480)))
        self.setPixmap(convert_cv_qt(self.img, width=480, height=800))
    
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        #self.thread_pool.start(self.run_selectors)
        self.sel = QPixelWidget(self.img[:, 0:640], self.img[:,640:1280], StereoParameters.load('stereo-pool'))
        self.sel.show()

    def run_selectors(self):
        #selector = PixelSelector(self.img[:, 0:640], self.img[:,640:1280], StereoParameters.load('stereo-pool'))
        coord1 = self.get_coord()
        if coord1 is not None:
            #selector = PixelSelector(self.img[:, 0:640], self.img[:,640:1280], StereoParameters.load('stereo-pool'))
            coord2 = self.get_coord()

            if coord2 is not None:
                self.coord1 = coord1
                self.coord2 = coord2

                img_annotated = draw_crosshairs(self.img, coord1.xl, coord1.y, thickness=5)
                img_annotated = draw_crosshairs(img_annotated, coord1.xr + 640, coord1.y, thickness=5)
                img_annotated = draw_crosshairs(img_annotated, coord2.xl, coord2.y, color=(0,120,255), thickness=5)
                img_annotated = draw_crosshairs(img_annotated, coord2.xr + 640, coord2.y, color=(0,120,255), thickness=5)
                self.setPixmap(convert_cv_qt(img_annotated, width=480, height=800))
                self.distance()
            else:
                self._clear_coords()
        else:
            self._clear_coords()
    
    def get_coord(self):
        queue = Queue()
        img_l = left_half(self.img)
        print('Original')
        print(img_l)
        img_r = right_half(self.img)

        arr_l = SharedMemory(create=True, size=img_l.shape[0] * img_l.shape[1] * img_l.shape[2])
        arr_r = SharedMemory(create=True, size=img_r.shape[0] * img_r.shape[1] * img_r.shape[2])
        print('Flattened data')
        print(img_l.flatten().data)
        arr_l.buf[:] = img_l.flatten().data[:]
        arr_r.buf[:] = img_r.flatten().data[:]

        print(f'ORIGINAL TYPE: {img_l.dtype}')

        process = Process(target=run_selector, args=(arr_l, arr_r, img_l.shape, img_r.shape, queue))
        process.start()
        return queue.get()

    def _clear_coords(self):
        self.coord1 = None
        self.coord2 = None
        self.setPixmap(convert_cv_qt(self.img, width=480, height=800))
        
    def distance(self):
        if self.coord1 is not None and self.coord2 is not None:
            point1 = self.params.triangulate_stereo_coord(self.coord1)
            point2 = self.params.triangulate_stereo_coord(self.coord2)
            print(point1)
            print(point2)
            dist = math.dist(point1, point2)
            print(dist)
            return dist
        else:
            return None