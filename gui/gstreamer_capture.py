from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import time
import datetime

import numpy as np

import cv2

from logger import root_logger

logger = root_logger.getChild(__name__)

def run_gstreamer_capture(pipeline: str, connection: Connection):
    time.sleep(5)
    while True:
        capture = None
        try:
            capture = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            while True:
                ret, cv_img = capture.read()
                if ret:
                    print(f'SENDING {cv_img.shape} {cv_img.dtype}')
                    #connection.send((cv_img, time.time_ns() ))
                    connection.send_bytes(cv_img.data, size=len(cv_img.data))
                    print('SENT')
        except Exception as e:
            print(f'EXCEPTION: {e}')
        finally:
            if capture is not None:
                capture.release()
            time.sleep(1)
                

class GstreamerCapture:

    def __init__(self, pipeline: str):
        self._recv_connection, send_connection = Pipe(False)
        self._buffer = bytearray(600 * 800 * 3)
        logger.info('Spawning Gstreamer subprocess')
        self._process = Process(target=run_gstreamer_capture, args=(pipeline, send_connection))
        self._process.start()

    def read(self):
        self._buffer = bytearray(600 * 800 * 3)
        ret = False
        img = None
        
        print('CHECKING1')
        poll = self._recv_connection.poll()
        print(f'Poll returned: {poll}')
        if poll:
            
            print('NOW RECEIVING')
            #img, time_ns = self._recv_connection.recv()
            try:
                ret = True
                self._recv_connection.recv_bytes_into(self._buffer)
                print('RECEIVED')
                img = np.frombuffer(self._buffer, dtype=np.uint8)
                img = img.reshape((600, 800, 3))

                #print(f'CHECKING AGAIN {img.dtype}')
                #print(time.time_ns() - time_ns)
            except Exception as e:
                print(f'RECV EXCEPTION {e}')
        
        print(f'RETURNING')
        return ret, img
    
    def release(self):
        self._process.kill()
    
