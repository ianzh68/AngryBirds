
####################################
# Button class
####################################

class Button(object):
    
    def __init__(self):
        self.mouseOnButton = False
        self.broder = 3

class RectButton(Button):

    def __init__(self, left, top, width, height, image):
        super().__init__()
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.image = image
        self.right = left + width
        self.bot = top + height
        self.bounds = [self.left, self.top, self.right, self.bot]
        self.background = [self.left - self.broder, self.top - self.broder,
                           self.width+2*self.broder, self.height+2*self.broder]
        self.chosenColor = (255, 255, 0)
        self.normalColor = (0, 0, 0)

class CircleButton(Button):

    def __init__(self, cx, cy, radius, image):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.image = image
        self.left = self.cx - self.image.get_width()//2
        self.top = self.cy - self.image.get_height()//2
        self.mouseOnButton = False

