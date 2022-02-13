"""Opens window with the transect line diagram and lets you manually map the wreck"""

import cv2
import os
import numpy as np
from util import data_path    

class MapWreck():
    def __init__(self):
        self.canvas = self.new_canvas()
        self.preview = self.canvas.copy()

        self.drawing = False
        self.line_color = (71, 93, 166)

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

    def new_canvas(self):
        """Creating the canvas"""

        final = 255 * np.ones(shape=[1000, 1000, 3], dtype=np.uint8)

        # Get transect line image from data repo
        transect_path = os.path.join(data_path, "transect", "transect_line.png") 
        transect_img = cv2.imread(transect_path, cv2.IMREAD_UNCHANGED)

        # Make transparent background white
        transect_mask = transect_img[:,:,3] == 0
        transect_img[transect_mask] = [255, 255, 255, 255]

        transect_img = cv2.cvtColor(transect_img, cv2.COLOR_BGRA2BGR)

        # Overlaying the transect image onto the final image
        x_offset = 0
        y_offset = 200

        x_end = x_offset + transect_img.shape[1]
        y_end = y_offset + transect_img.shape[0]

        final[y_offset:y_end,x_offset:x_end] = transect_img

        return final

    def draw(self, event, x, y, flags, param):
        """Draws a line on the screen based on mouse clicks"""

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing == False:
                # Save mouse position of the first click

                self.x1, self.y1 = x, y
                self.drawing = True

            else: 
                # Save mouse posiiton of the second click

                self.x2, self.y2 = x, y
                self.drawing = False

                # Draw the line on the actual canvas
                cv2.line(self.canvas, (self.x1, self.y1), (self.x2, self.y2), self.line_color, thickness=6)

        if event == cv2.EVENT_RBUTTONDOWN:
            # Delete line currently being drawn

            self.drawing = False

        if self.drawing == True:
            # Show the line being drawn on the screen

            self.preview = self.canvas.copy()
            cv2.line(self.preview, (self.x1, self.y1), (x, y), self.line_color, thickness=6)

    def show_canvas(self):
        """Display the canvas"""

        window = "Map Wreck"

        while True:

            cv2.setMouseCallback(window, self.draw)

            if self.drawing == False:
                cv2.imshow(window, self.canvas)

            else:
                cv2.imshow(window, self.preview)

            cv2.setWindowProperty(window, cv2.WND_PROP_TOPMOST, 1)

            key = cv2.waitKey(1) & 0xFF

            # 'q' key to exit
            if key == ord("q"):
                break

            # 'c' key to clear the window
            elif key == ord("c"):
                self.canvas = self.new_canvas()
                self.preview = self.canvas.copy()

        cv2.destroyAllWindows()
