import os, sys
from PyQt5.QtWidgets import QApplication
from gui.app import App
from gui.theme import *
from util import data_path
import argparse

import os

if 'QT_QPA_PLATFORM_PLUGIN_PATH' in os.environ:
    os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH')

#run commands from terminal
parser = argparse.ArgumentParser(description='Run the GUI')
parser.add_argument('-theme', type=str, help='choose a theme: dark_theme')
args = parser.parse_args()

app = QApplication(sys.argv)
theme_picker(app, args.theme)
a = App([os.path.join(data_path, 'example-streams', '1.mp4'), os.path.join(data_path, 'example-streams', '2.mp4')])
a.show()
sys.exit(app.exec_())