import os, sys
from PyQt5.QtWidgets import QApplication

from gui.app import App
from vision import data_path

app = QApplication(sys.argv)
a = App(os.path.join(data_path, 'example-streams', '1.mp4'))
a.show()
sys.exit(app.exec_())