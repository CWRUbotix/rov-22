from sys import stdout
from PyQt5 import QtGui
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget


class ImageControlsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self.prev_image_button = QPushButton(self)
        self.prev_image_button.setText("<")
        self.horizontal_layout.addWidget(self.prev_image_button)

        self.next_image_button = QPushButton(self)
        self.next_image_button.setText(">")
        self.horizontal_layout.addWidget(self.next_image_button)

        self.setLayout(self.horizontal_layout)