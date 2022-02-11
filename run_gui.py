import argparse
import os
import sys

from PyQt5.QtWidgets import QApplication
import cv2

from gui.app import App
from gui.theme import *
from gui.data_classes import VideoSource
from util import config_parser, data_path


def parse_args(arg_list):
    parser = argparse.ArgumentParser(description='Run the GUI')
    parser.add_argument('-t', '--theme', type=str, help='choose a theme: dark_theme, alt_theme')
    parser.add_argument('-c', '--cameras', type=config_parser('camera'), help='The camera configuration file to use located in camera/config')
    parser.add_argument('-f', '--fullscreen', action='store_true', help='Runs the app in fullscreen mode')
    return parser.parse_args(arg_list)

def run_gui(args):
    if 'QT_QPA_PLATFORM_PLUGIN_PATH' in os.environ:
        os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH')

    app = QApplication(sys.argv)
    theme_picker(app, args.theme)
    a = App(args)

    a.show()
    return app.exec_()

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    run_gui(args)
