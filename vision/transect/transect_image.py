"""For storing the eight transect images"""

class TransectImage():

    def __init__(self, num, image):
        self.num = num
        self.image = image
        
        self.vertical_lines = []
        self.horizontal_lines = []

    
