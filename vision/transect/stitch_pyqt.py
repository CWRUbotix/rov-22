import numpy as np
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from vision.transect.stitch_transect import *
from gui.gui_util import convert_cv_qt
from logger import root_logger

logger = root_logger.getChild(__name__)

class TransectStitcherWidget(QWidget):
    stitched_image_signal = pyqtSignal(np.ndarray)

    def __init__(self, stitcher):
        super().__init__()

        self.stitcher = stitcher
        self.image_index = 0

    def initUI(self):
        self.image_list = self.stitcher.get_images()
        self.transect_img = self.stitcher.images[self.image_index]

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.setWindowTitle("Transect Stitching")
        self.display_image(self.stitcher.images[self.image_index].image)
        self.show()

    def display_image(self, image):
        pixmap = QPixmap(convert_cv_qt(image))
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())

        self.show()
        logger.info(f"Displaying transect square {self.image_index+1}")

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Right and self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.transect_img = self.stitcher.images[self.image_index]
            self.display_image(self.transect_img.image)

        elif key == Qt.Key_Left and self.image_index > 0:
            self.image_index -= 1
            self.transect_img = self.stitcher.images[self.image_index]
            self.display_image(self.transect_img.image)

        elif key == Qt.Key_R:
            self.transect_img.coords = []
            logger.info(f"RESETTING SQUARE {self.transect_img.num+1} POINTS")

        elif key == Qt.Key_Return:

            for key in self.stitcher.images:
                trans = self.stitcher.images[key]

                if len(trans.coords) != 4:
                    logger.info(f"WARNING: Square {key+1} does not have 4 points selected")
                    return

            self.stitch_manually()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        x = ev.localPos().x()
        y = ev.localPos().y()   

        self.transect_img.coords.append((x, y))
        logger.info(f"Square {self.transect_img.num+1} coord {len(self.transect_img.coords)}: ({x}, {y})")

    def stitch_manually(self):
        cropped = cropped_images(self.stitcher)
        final_image = final_stitched_image(cropped)
        self.stitched_image_signal.emit(final_image)

        self.display_image(final_image)

# if __name__ == '__main__':
#     stitcher = TransectStitcher()

#     folder_path = os.path.join(data_path, "transect", "stitching", "p00l")

#     files = [img_name for img_name in os.listdir(folder_path)]
#     files.sort()

#     image_path = os.path.join(folder_path, files[0])

#     for i in range(0, 8):
#         image_path = os.path.join(folder_path, files[i])

#         image = TransectImage(i, cv2.imread(image_path))
#         stitcher.set_image(i, image)

#     app = QApplication(sys.argv)

#     demo = TransectStitcher(stitcher)
#     demo.show()

#     sys.exit(app.exec_())