"""
Opens a window with the wreck and lets you manually resize the image.

Left click to set crop corners
Right click to delete the last corner
'q' to quit
'c' to clear the window
"""

import cv2
import os
import numpy as np
from util import data_path    

class WreckLength():
    def __init__(self):
        self.canvas = self.new_canvas()
        self.preview = self.canvas.copy()

        self.clickList = []
        self.drawing = False
        self.crop = False
        self.line_color = (71, 93, 166)

        self.IMAGE_SIZE = 800

    def new_canvas(self):
        """Creating the canvas"""

        # Get transect line image from data repo
        img_path = os.path.join(data_path, "transect", "stitching", "B", "3", "20220222_184317.jpg") 
        image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

        # Make transparent background white
        #mask = image[:,:,3] == 0
        #image[mask] = [255, 255, 255, 255]

        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        resized = cv2.resize(image, (800, 800), interpolation = cv2.INTER_AREA)


        return resized

    def draw(self, event, x, y, flags, param):
        """Draws a line on the screen based on mouse clicks. Make sure to click in order [Top Left, Bottom Left, bottom Right, Bottom Right!"""
        #clickList = []
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing == False:
                # Save mouse position of the first four clicks
                if self.crop == False:
                    self.clickList.append([x,y])
                print(len(self.clickList))
                if len(self.clickList) >= 4:
                    if self.crop == True:
                        # Find perspective transform matrix
                        src = np.float32([[self.clickList[3][0], self.clickList[3][1]], [self.clickList[2][0], self.clickList[2][1]], [self.clickList[0][0], self.clickList[0][1]], [self.clickList[1][0], self.clickList[1][1]]])
                        dst = np.float32([[0, self.IMAGE_SIZE], [self.IMAGE_SIZE, self.IMAGE_SIZE], [0, 0], [self.IMAGE_SIZE, 0]])
                        matrix = cv2.getPerspectiveTransform(src, dst)
                        # Perspective transform original image
                        warped = cv2.warpPerspective(self.canvas, matrix, (self.IMAGE_SIZE, self.IMAGE_SIZE))
                        self.canvas = warped
                        self.crop = False
                    else:
                        self.drawing = True
            else:
                # Draw the line on the actual canvas
                self.preview = self.canvas.copy()
                for x in range (0,3):
                    cv2.line(self.preview, (self.clickList[x][0],self.clickList[x][1]),(self.clickList[x+1][0],self.clickList[x+1][1]), self.line_color, thickness= 6)
                cv2.line(self.preview, (self.clickList[3][0],self.clickList[3][1]),(self.clickList[0][0],self.clickList[0][1]), self.line_color, thickness= 6)
                #cv2.rectangle(self.preview, (self.clickList[0][0],self.clickList[0][1]), (self.clickList[2][0], self.clickList[2][1]), (0, 0, 0), 5)
                cv2.imshow('image', self.preview)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                self.drawing = False
                self.crop = True
                
        if event == cv2.EVENT_RBUTTONDOWN:
            # Delete line currently being drawn
            self.clickList.pop()
            self.drawing = False
            self.crop = False

    def show_canvas(self):
        """Display the canvas"""

        window = "Wreck Length"

        while True:
            if self.drawing == False:
                cv2.imshow(window, self.canvas)

           # else:
            #    cv2.imshow(window, self.preview)

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

    mapper = WreckLength()
    mapper.show_canvas()
