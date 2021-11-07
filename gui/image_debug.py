from PyQt5.QtGui import QSurfaceFormat
import cv2
from gui.gui_util import convert_cv_qt
import os, sys
from typing import List
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QGraphicsGridLayout, QGraphicsLayoutItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsWidget, QGridLayout, QLabel, QOpenGLWidget, QWidget
from util import data_path


class ImagesWidget(QGraphicsView):

    folder = os.path.join(data_path, 'example-images', 'star')
    #
    
    def __init__(self):
        self.scene = QGraphicsScene()
        super().__init__(self.scene)

        gl = QOpenGLWidget()
        #gl.setFormat(format)
        #self.setViewport(gl)

        self.threadpool = QThreadPool()

        self.filenames = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if os.path.isfile(os.path.join(self.folder, f))]
        #print(self.filenames)
        grid = QGraphicsGridLayout()
        

        self.image_pixmaps: List[QGraphicsPixmapItem] = []
        self.image_cache: List = []

        for filename in self.filenames:
            self.image_cache.append(cv2.imread(filename))

        for i in range(4):
            for j in range(4):
                pixmapItem = QGraphicsPixmapItem()
                pixmapItem.setOffset(200 * i, 200 * j)
                self.image_pixmaps.append(pixmapItem)
                self.scene.addItem(pixmapItem)

        self.threadpool

    def load_images(self):
        for i in range(16):
            self.image_pixmaps[i].setPixmap(convert_cv_qt(self.image_cache[i], 200, 200))


        




if __name__ == '__main__':
    if 'QT_QPA_PLATFORM_PLUGIN_PATH' in os.environ:
        os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH')
    app = QApplication(sys.argv)
    a = ImagesWidget()
    a.show()
    sys.exit(app.exec_())