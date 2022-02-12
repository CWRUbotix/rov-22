import cv2
import numpy as np

class MapWreck():
    def __init__(self):
        self.canvas = 255 * np.ones(shape=[512, 512, 3], dtype=np.uint8)
        self.preview = self.canvas.copy()

        self.drawing = False

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        self.point1 = [self.x1, self.y1]
        self.point2 = [self.x2, self.y2]

    def draw(self, event, x, y, flags, param):

        if self.drawing == True:
            self.preview = self.canvas.copy()

            cv2.line(self.preview, self.point1, (x, y), (0, 255, 0), thickness=2)

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.drawing == False:

                self.x1, self.y1 = x, y
                self.point1 = [x, y]
                
                self.drawing = True

            else: 
                self.x2, self.y2 = x, y

                self.point2 = [x, y]
                self.drawing = False

                print(f'{self.x1}, {self.y1}')
                print(f'{self.x2}, {self.y2}')

                cv2.line(self.canvas, self.point1, self.point2, (0, 255, 0), thickness=2)

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
            # 'q' to quit
            if key == ord("q"):
                break

        cv2.destroyAllWindows()


mapper = MapWreck()

mapper.show_canvas()
