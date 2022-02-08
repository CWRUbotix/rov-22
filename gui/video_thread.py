import os
import cv2
import json

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from cv2 import CAP_GSTREAMER

from gui.data_classes import Frame, VideoSource
from util import data_path


class VideoThread(QThread):
    update_frames_signal = pyqtSignal(Frame)

    def __init__(self, video_sources):
        super().__init__()
        self._thread_running_flag = True
        self._video_playing_flag = True
        self._restart = False

        self._video_sources = video_sources
        self._captures = []
        self._rewind = False

    def _prepare_captures(self):
        """Initialize video capturers from self._video_sources"""
        for source in self._video_sources:
            self._captures.append(cv2.VideoCapture(source.filename, source.api_preference))

    def _emit_frames(self):
        """Emit next/prev frames on the pyqtSignal to be received by video widgets"""

        # Restart the videos if restart is true
        if self._restart:
            for index, capture in enumerate(self._captures):
                if self._video_sources[index].api_preference != CAP_GSTREAMER:  # don't restart gstreams
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            self._restart = False

        for index, capture in enumerate(self._captures):

            if self._rewind and self._video_sources[index].api_preference != CAP_GSTREAMER:  # don't rewind gstreams
                prev_frame = cur_frame = capture.get(cv2.CAP_PROP_POS_FRAMES)

                if cur_frame >= 2:
                    # Go back 2 frames so when we read() we'll read back 1 frame
                    prev_frame -= 2
                else:
                    # If at beginning, just read 1st frame over and over
                    prev_frame = 0

                capture.set(cv2.CAP_PROP_POS_FRAMES, prev_frame)

            # Read the frame
            ret, cv_img = capture.read()
            if ret:
                self.update_frames_signal.emit(Frame(cv_img, index))

    def run(self):
        self._prepare_captures()

        # Run the play/pausable video
        while self._thread_running_flag:
            # Send frames if the video is playing
            if self._video_playing_flag:
                self._emit_frames()

            # Wait if playing normally, don't if rewinding b/c rewinding is slow
            if not self._rewind:
                self.msleep(int(1000 / 30))

        # Shut down capturers
        for capture in self._captures:
            capture.release()

    def next_frame(self):
        """Goes forward a frame if the video is paused"""
        if not self._video_playing_flag:
            prev_rewind_state = self._rewind
            self._rewind = False
            self._emit_frames()
            self._rewind = prev_rewind_state

    def prev_frame(self):
        """Goes back a frame if the video is paused"""
        if not self._video_playing_flag:
            prev_rewind_state = self._rewind
            self._rewind = True
            self._emit_frames()
            self._rewind = prev_rewind_state

    def toggle_rewind(self):
        """Toggles the video rewind flag"""
        self._rewind = not self._rewind

    def toggle_play_pause(self):
        """Toggles the video playing flag"""
        self._video_playing_flag = not self._video_playing_flag

    def stop(self):
        """Sets the video playing & thread running flags to False and waits for thread to end"""
        self._video_playing_flag = False
        self._thread_running_flag = False
        self.wait()

    def restart(self):
        """Restarts the video from the beginning"""
        self._restart = True

    @pyqtSlot(list)
    def on_select_filenames(self, filenames):
        """Adds all files specified in .json arrays or by selecting actual files"""

        self._video_sources = []

        for filename in filenames:
            if os.path.splitext(filename)[1] == ".json":
                file = open(filename, "r")
                json_data = json.load(file)

                if json_data["sources"]:
                    for source in json_data["sources"]:
                        api = cv2.CAP_FFMPEG
                        if source["api"] == "gstreamer":
                            api = cv2.CAP_GSTREAMER
                        else:
                            source["name"] = os.path.join(data_path, source["name"])
                        
                        self._video_sources.append(VideoSource(source["name"], api))

                file.close()
            else:
                self._video_sources.append(VideoSource(filename, cv2.CAP_FFMPEG))

        self._video_playing_flag = True
        self._captures = []
        self._rewind = False
        self._prepare_captures()