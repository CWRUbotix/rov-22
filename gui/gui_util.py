from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import cv2


def convert_cv_qt(cv_img, width=None, height=None):
    """Convert from an opencv image to QPixmap"""

    if len(cv_img.shape) == 3:
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = cv_img.shape
        bytes_per_line = ch * w

        img_format = QtGui.QImage.Format_RGB888

    elif len(cv_img.shape) == 2:
        h, w = cv_img.shape
        bytes_per_line = w

        img_format = QtGui.QImage.Format_Grayscale8

    convert_to_Qt_format = QtGui.QImage(cv_img.data, w, h, bytes_per_line, img_format)

    if width is not None:
        convert_to_Qt_format = convert_to_Qt_format.scaled(width, height, Qt.KeepAspectRatio)

    return QtGui.QPixmap.fromImage(convert_to_Qt_format)