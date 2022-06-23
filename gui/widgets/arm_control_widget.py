from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton


ARM_STYLE = "QPushButton { background-color: green }"
DISARM_STYLE = "QPushButton { background-color: red }"
DISABLED_STYLE = "QPushButton { background-color: #575757 }"


class ArmControlWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.root_layout = QHBoxLayout(self)
        self.setLayout(self.root_layout)

        arm_button = QPushButton("Arm", self)
        disarm_button = QPushButton("Disarm", self)

        arm_button.setMinimumHeight(70)
        disarm_button.setMinimumHeight(70)

        disarm_button.setStyleSheet(DISARM_STYLE)

        button_font = QFont('Arial', 24)
        arm_button.setFont(button_font)
        disarm_button.setFont(button_font)

        self.arm_button = arm_button
        self.disarm_button = disarm_button
        self.on_disconnect()

        self.root_layout.addWidget(self.arm_button)
        self.root_layout.addWidget(self.disarm_button)

    def on_arm(self):
        self.arm_button.setEnabled(False)
        self.disarm_button.setEnabled(True)
        self.arm_button.setStyleSheet(ARM_STYLE)
        self.disarm_button.setStyleSheet("")

    def on_disarm(self):
        self.arm_button.setEnabled(True)
        self.disarm_button.setEnabled(False)
        self.arm_button.setStyleSheet("")
        self.disarm_button.setStyleSheet(DISARM_STYLE)

    def on_connect(self):
        self.on_disarm()

    def on_disconnect(self):
        self.arm_button.setEnabled(False)
        self.disarm_button.setEnabled(False)
        self.arm_button.setStyleSheet(DISABLED_STYLE)
        self.disarm_button.setStyleSheet(DISABLED_STYLE)
