from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


class VehicleStatusWidget(QLabel):
    def __init__(self):
        super().__init__()

        self.connected = False
        self.task = ""

        self.setFont(QFont("Sans Serif", 12))
        self.setStyleSheet("padding-left: 10 px")
        self.update_text()

    def update_text(self):
        self.setText(f"Mavlink: {'Connected' if self.connected else 'Disconnected'}\n"
                     f"Task: {'None' if self.task == '' else self.task}"
                     )

    def on_task_change(self, new_task):
        self.task = new_task
        self.update_text()

    def on_connect(self):
        self.connected = True
        self.update_text()

    def on_disconnect(self):
        self.connected = False
        self.update_text()
