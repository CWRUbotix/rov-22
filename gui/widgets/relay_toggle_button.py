from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QLabel


class RelayToggleButton(QPushButton):
    state_change_signal = pyqtSignal(bool)

    def __init__(self, text, parent=None, control_prompt_image=None):
        super().__init__(text, parent)

        self.setFixedHeight(50)
        self.setCheckable(True)
        self.clicked.connect(self.send_state)
        self.disable_click()

        self.control_prompt = QLabel()
        self.control_prompt.setFixedHeight(50)
        if control_prompt_image is not None:
            self.control_prompt.setPixmap(control_prompt_image)

    def send_state(self):
        if self.isChecked():
            self.relay_on()
        else:
            self.relay_off()

    def toggle(self):
        if self.isEnabled():
            super().toggle()
            self.send_state()

    def relay_off(self):
        self.setChecked(False)
        self.state_change_signal.emit(False)

    def relay_on(self):
        self.setChecked(True)
        self.state_change_signal.emit(True)

    def enable_click(self):
        self.setEnabled(True)
        self.setStyleSheet("QPushButton:checked { background-color: blue }")

    def disable_click(self):
        self.setEnabled(False)
        self.setStyleSheet("QPushButton { background-color: #575757 }"
                           "QPushButton:checked { background-color: #5f5fff }")

    def on_disarm(self):
        self.relay_off()
        self.disable_click()

