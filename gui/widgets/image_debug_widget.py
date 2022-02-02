from PyQt5.QtGui import QSurfaceFormat
import cv2
import numpy as np
from gui.gui_util import convert_cv_qt
import os, sys
from typing import List
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QGraphicsGridLayout, QGraphicsLayoutItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsWidget, QGridLayout, QLabel, QOpenGLWidget, QWidget
from util import data_path

IMAGE_SIZE = 200

class PixmapItem(QGraphicsPixmapItem):

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        pass

class ImagesWidget(QGraphicsView):

    image_pixmaps: List[PixmapItem] = []
    image_cache: List[np.ndarray] = []
    
    def __init__(self):
        self.scene = QGraphicsScene()
        super().__init__(self.scene)

        self.threadpool = QThreadPool()

        for i in range(4):
            for j in range(4):
                pixmapItem = PixmapItem()
                pixmapItem.setOffset(IMAGE_SIZE * i, IMAGE_SIZE * j)
                self.image_pixmaps.append(pixmapItem)
                self.scene.addItem(pixmapItem)
    
    def set_folder(self, folder: str):
        self.folder = folder
        self.filenames = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if os.path.isfile(os.path.join(self.folder, f))]
        self.image_cache = []
        for filename in self.filenames:
            self.image_cache.append(cv2.imread(filename))
        self.load_images()

    def load_images(self):
        for i in range(16):
            self.image_pixmaps[i].setPixmap(convert_cv_qt(self.image_cache[i], IMAGE_SIZE, IMAGE_SIZE))