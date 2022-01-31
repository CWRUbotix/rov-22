from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton


class ArmControlWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        arm_button = QPushButton("Arm", self)
        disarm_button = QPushButton("Disarm", self)

        arm_button.setCheckable(True)
        disarm_button.setCheckable(True)
        disarm_button.setChecked(True)
        disarm_button.setEnabled(False)

        arm_button.setMinimumHeight(100)
        disarm_button.setMinimumHeight(100)

        arm_button.setStyleSheet("QPushButton:checked { background-color: green }")
        disarm_button.setStyleSheet("QPushButton:checked { background-color: red }")

        button_font = QFont('Arial', 24)
        arm_button.setFont(button_font)
        disarm_button.setFont(button_font)

        arm_button.clicked.connect(self.on_arm_clicked)
        disarm_button.clicked.connect(self.on_disarm_clicked)

        self.arm_button = arm_button
        self.disarm_button = disarm_button

        self.root_layout.addWidget(self.arm_button)
        self.root_layout.addWidget(self.disarm_button)

    def on_arm_clicked(self):
        self.arm_button.setEnabled(False)
        self.disarm_button.setEnabled(True)
        self.disarm_button.setChecked(False)

    def on_disarm_clicked(self):
        self.disarm_button.setEnabled(False)
        self.arm_button.setEnabled(True)
        self.arm_button.setChecked(False)
