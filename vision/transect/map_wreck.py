import cv2
import os
import numpy as np
from util import data_path    

class MapWreck():
    def __init__(self):
        self.canvas = self.set_canvas()
        self.preview = self.canvas.copy()

        self.drawing = False
        self.line_color = (71, 93, 166)

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        self.point1 = [self.x1, self.y1]
        self.point2 = [self.x2, self.y2]

    def set_canvas(self):

        # Overlaying the transect image onto the final image
        final = 255 * np.ones(shape=[1000, 1000, 3], dtype=np.uint8)

        transect_path = os.path.join(data_path, "transect", "transect_line.png") 
        transect_img = cv2.imread(transect_path, cv2.IMREAD_UNCHANGED)

        transect_mask = transect_img[:,:,3] == 0
        transect_img[transect_mask] = [255, 255, 255, 255]

        transect_img = cv2.cvtColor(transect_img, cv2.COLOR_BGRA2BGR)

        x_offset = 0
        y_offset = 200

        x_end = x_offset + transect_img.shape[1]
        y_end = y_offset + transect_img.shape[0]

        final[y_offset:y_end,x_offset:x_end] = transect_img

        return final

    def draw(self, event, x, y, flags, param):

        if self.drawing == True:
            self.preview = self.canvas.copy()
            cv2.line(self.preview, self.point1, (x, y), self.line_color, thickness=2)

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing == False:

                self.x1, self.y1 = x, y
                self.point1 = [x, y]
                
                self.drawing = True

            else: 
                self.x2, self.y2 = x, y

                self.point2 = [x, y]
                self.drawing = False

                cv2.line(self.canvas, self.point1, self.point2, self.line_color, thickness=2)

            print(self.drawing)

        if event == cv2.EVENT_RBUTTONDOWN:
            self.drawing = False

    def show_canvas(self):
        while True:

            cv2.setMouseCallback("image", self.draw)

            if self.drawing == False:
                cv2.imshow("image", self.canvas)

            else:
                cv2.imshow("image", self.preview)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        cv2.destroyAllWindows()
        

mapper = MapWreck()
mapper.show_canvas()
