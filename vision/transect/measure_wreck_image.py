import math
from PyQt5.QtWidgets import QLabel

class MeasureWreckImage(QLabel):

    def __init__(self, distLabel):
        super().__init__()

        self.setObjectName('image')

        self.distLabel = distLabel

        self.points = []

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
            
        if len(self.points) == 2:
            self.points = []

        self.points.append({'x': x, 'y': y})
        self.distLabel.setText('Click another')

        if len(self.points) == 2:
            dist = self.get_dist()

            # TODO: Convert pixel get_dist into real-world length

            self.distLabel.setText(
                '(' + str(self.points[0]['x']) + ',' + str(self.points[0]['y']) + ') -> (' +
                str(self.points[1]['x']) + ',' + str(self.points[1]['y']) + '): ' +
                str(dist)
            )
        
        self.distLabel.repaint()
    
    def get_dist(self):
        return math.sqrt( (self.points[1]['x'] - self.points[0]['x']) ** 2 + (self.points[1]['y'] - self.points[0]['y']) ** 2 )