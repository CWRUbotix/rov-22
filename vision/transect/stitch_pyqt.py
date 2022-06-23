import os
import sys
import cv2
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from util import data_path
from vision.transect.stitch_transect import *
from vision.transect.transect_image import TransectImage
from gui.gui_util import convert_cv_qt

class MainWindow(QWidget):
    def __init__(self, stitcher):
        super().__init__()

        self.stitcher = stitcher
        self.image_list = stitcher.get_images()
        self.image_index = 0
        self.transect_img = stitcher.images[self.image_index]
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border-color: transparent;")        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.setWindowTitle("Transect Stitching")
        self.display_image(stitcher.images[self.image_index].image)
        self.show()

    def display_image(self, image):
        pixmap = QPixmap(convert_cv_qt(image))
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())

        self.show()

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Right and self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.transect_img = stitcher.images[self.image_index]
            self.display_image(self.transect_img.image)

        elif key == Qt.Key_Left and self.image_index > 0:
            self.image_index -= 1
            self.transect_img = stitcher.images[self.image_index]
            self.display_image(self.transect_img.image)

        elif key == Qt.Key_R:
            print(f"RESETTING SQUARE {self.transect_img.num} POINTS")
            self.transect_img.coords = []

        elif key == Qt.Key_Return:
            self.stitch_manually()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        x = ev.localPos().x()
        y = ev.localPos().y()   

        self.transect_img.coords.append((x, y))
        print(f"Square {self.transect_img.num} coord {len(self.transect_img.coords)}: ({x}, {y})")        

    def stitch_manually(self):
        cropped = cropped_images(self.stitcher)
        final_image = final_stitched_image(cropped)

        self.display_image(final_image)

if __name__ == '__main__':
    stitcher = StitchTransect()

    folder_path = os.path.join(data_path, "transect", "stitching", "p00l")

    files = [img_name for img_name in os.listdir(folder_path)]
    files.sort()

    image_path = os.path.join(folder_path, files[0])

    image_list = []

    for i in range(0, 8):
        image_path = os.path.join(folder_path, files[i])

        image = TransectImage(i, cv2.imread(image_path))
        stitcher.set_image(i, image)
        image_list.append(image_path)

    app = QApplication(sys.argv)

    demo = MainWindow(stitcher)
    demo.show()

    sys.exit(app.exec_())