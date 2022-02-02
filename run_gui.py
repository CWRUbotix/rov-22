import argparse
import os
import sys

from PyQt5.QtWidgets import QApplication
import cv2

from gui.app import App
from gui.theme import *
from gui.data_classes import VideoSource
from util import data_path

if 'QT_QPA_PLATFORM_PLUGIN_PATH' in os.environ:
    os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH')

# run commands from terminal
parser = argparse.ArgumentParser(description='Run the GUI')
parser.add_argument('-theme', type=str, help='choose a theme: dark_theme, alt_theme')
args = parser.parse_args()

app = QApplication(sys.argv)
theme_picker(app, args.theme)
a = App([
        VideoSource(os.path.join(data_path, 'example-streams', '1.mp4'), cv2.CAP_FFMPEG),
        VideoSource(os.path.join(data_path, 'example-streams', '2.mp4'), cv2.CAP_FFMPEG),
        VideoSource(os.path.join(data_path, 'example-streams', '1.mp4'), cv2.CAP_FFMPEG),
        VideoSource('udpsrc port=5600 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
    ])

print(os.path.join(data_path, 'example-streams', '1.mp4'))

a.show()
sys.exit(app.exec_())
