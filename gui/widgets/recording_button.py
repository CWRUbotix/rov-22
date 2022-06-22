import subprocess
import atexit

from PyQt5.QtWidgets import QPushButton


class RecordingButton(QPushButton):

    def __init__(self):
        super().__init__()

        self.process = None

        self.setText("Start Recording")
        self.setCheckable(True)

        self.clicked.connect(self.on_click)

        atexit.register(lambda: self.process.kill())

    def on_click(self):
        if self.isChecked():
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.setChecked(True)
        self.setText("🔴 Stop Recording")
        self.process = subprocess.Popen(["obs", "--startrecording", "--minimize-to-tray"], shell=False)

    def stop_recording(self):
        self.process.kill()
        self.setText("Start Recording")

