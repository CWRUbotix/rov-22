from multiprocessing import Process, Event
from multiprocessing.shared_memory import SharedMemory
import time

import numpy as np

import cv2

from logger import root_logger

logger = root_logger.getChild(__name__)

def run_gstreamer_capture(pipeline: str, new_frame_event, shared_buffer: SharedMemory):
    while True:
        capture = None
        try:
            capture = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            while True:
                new_frame_event.wait()
                ret, cv_img = capture.read()
                if ret:
                    flat = cv_img.view()
                    flat.shape = (shared_buffer.size)
                    shared_buffer.buf[:] = flat.data[:]
                    new_frame_event.clear()
        except Exception as e:
            print(f'Exception in gstreamer process: {e}')
        finally:
            if capture is not None:
                capture.release()
            time.sleep(1)
                

class GstreamerCapture:

    def __init__(self, pipeline: str, width: int, height: int):
        self._width = width
        self._height = height

        self._new_frame_event = Event()
        self._new_frame_event.set()
        self._shared_buffer = SharedMemory(create=True, size=(3 * width * height))

        logger.info('Spawning Gstreamer subprocess')
        self._process = Process(target=run_gstreamer_capture, args=(pipeline, self._new_frame_event, self._shared_buffer))
        self._process.start()

    def read(self):
        if not self._new_frame_event.is_set():
            img = np.frombuffer(self._shared_buffer.buf, dtype=np.uint8)
            img = img.reshape((self._height, self._width, 3))
            self._new_frame_event.set()
            return True, img

        return False, None
    
    def release(self):
        self._process.kill()
        self._shared_buffer.unlink()
