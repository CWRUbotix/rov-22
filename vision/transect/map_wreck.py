"""
Opens a window with the transect line diagram and lets you manually map the wreck.

Left click to start drawing a line and then click again to set the line.
Right click to delete the line you are currently drawing.
'q' to quit
'c' to clear the window
"""

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

        # Get transect line image from data repo
        img_path = os.path.join(data_path, "transect", "transect_line.png") 
        image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

        # Make transparent background white
        mask = image[:,:,3] == 0
        image[mask] = [255, 255, 255, 255]

        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)


        return image

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
            if self.drawing == False:
                cv2.imshow(window, self.canvas)

            else:
                cv2.imshow(window, self.preview)

            cv2.setMouseCallback(window, self.draw)
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

if __name__ == "__main__":

    mapper = MapWreck()
    mapper.show_canvas()
