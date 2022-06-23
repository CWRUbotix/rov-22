from lib2to3.pytree import convert
import cv2
from util import data_path
from gui.gui_util import convert_cv_qt
from vision.transect.measure_wreck_image import MeasureWreckImage
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout

class MeasureWreck(QWidget):
    def __init__(self, quit_thread, img = cv2.imread(data_path + '/transect/stitching/A/1/2022-06-16_131958.png')):
        super().__init__()

        self.pixmap = convert_cv_qt(img)
        
        self.quit_thread = quit_thread

        self.points = []

        self.setWindowTitle('Measure Wreck')

        self.layout = QVBoxLayout()

        self.distLabel = QLabel('Click endpoints')
        
        self.imageLabel = MeasureWreckImage(self.distLabel)
        self.imageLabel.setPixmap(self.pixmap)

        self.layout.addWidget(self.imageLabel)
        self.layout.addWidget(self.distLabel)
        self.setLayout(self.layout)
    

    def closeEvent(self, event):
        self.quit_thread()
        event.accept()