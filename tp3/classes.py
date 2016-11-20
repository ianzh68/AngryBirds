import pygame
from pygame.locals import *
from pygame.color import *
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "pymunk-4.0.0"))
import pymunk
from pymunk import Vec2d
import math
from sounds import *


####################################
# Common sharing helper functions
####################################

def rotateImage(p0, p1, image):
    x0, y0 = p0
    x1, y1 = p1
    if x1 < x0: 
        angle = math.atan((y1 - y0)/(x0 - x1))
    elif x1 > x0: 
        angle = -math.atan((y0 - y1)/(x0 - x1))
        image = pygame.transform.flip(image, True, False)
    else:
        if y1 < y0: angle = -1/2 * math.pi
        elif y1 > y0: angle = 1/2 * math.pi
        else: angle = 0
    angle = radian2degree(angle)
    image = pygame.transform.rotate(image, angle)
    return image

def radian2degree(angle):
    degree = 180
    return angle/math.pi * degree

def getDistance(x1, y1, x0, y0):
    distance = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1/2)
    return distance

def getPygameCoords(coordinate, data):
    # convert the given coordinate in pymunk to pygame
    return int(coordinate.x), int(data.height-coordinate.y)

def drawTemp(screen, x, y, image):
    x -= image.get_width()/2
    y -= image.get_height()/2
    screen.blit(image, (x, y)) 

def getImpulse(distance, data):
    if distance >= data.launchRadius:
        distance = data.launchRadius
    horizontal, vertical = 100, 0
    impulse = distance * Vec2d(horizontal, vertical)
    impulse[0] = round(impulse[0], 10)
    return impulse

def getLaunchAngle(data):
    if data.x1 < data.x0: 
        angle = math.atan((data.y1 - data.y0)/(data.x0 - data.x1))
    elif data.x1 > data.x0: 
        angle = math.pi - math.atan((data.y0 - data.y1)/(data.x0 - data.x1))
    else:
        if data.y1 < data.y0: angle = -1/2 * math.pi
        elif data.y1 > data.y0: angle = 1/2 * math.pi
        else: angle = 0
    return round(angle, 10)

def existObstacles(data, obj1, obj2):
    existRect = existRectObstacles(data, obj1, obj2)
    existCircle = existCircleObstacles(data, obj1, obj2)
    return existRect or existCircle

def existRectObstacles(data, obj1, obj2):
    try: p1 = (x1, y1) = obj1.body.position
    except: p1 = (obj1.x, obj1.y)
    try: p2 = (x2, y2) = obj2.body.position
    except: p2 = (obj2.x, obj2.y)
    for target in data.bricks:
        rect = (left, top, right, bot) = target.getBounds()
        result = rectBetweenPoints(p1, p2, rect)
        if result != False: return result
    return False

def existCircleObstacles(data, obj1, obj2):
    try: p1 = (x1, y1) = obj1.body.position
    except: p1 = (obj1.x, obj1.y)
    try: p2 = (x2, y2) = obj2.body.position
    except: p2 = (obj2.x, obj2.y)
    for target in data.objects:
        if type(target) == Stone:
            cx, cy = target.body.position
            radius = target.radius
            circle = (cx, cy, radius)
            result = circleBetweenPoints(p1, p2, circle)
            if result != False: return result
    return False

def rectBetweenPoints(p1, p2, rect):
    left, top, right, bot = rect
    diag1 = ((left, top), (right, bot))
    diag2 = ((left, bot), (right, top))
    line = (p1, p2)
    return linesIntersect(line, diag1) or linesIntersect(line, diag2)

def circleBetweenPoints(p1, p2, circle):
    cx, cy, radius = circle
    point = (cx, cy)
    line = (p1, p2)
    perpendicularLength = solvePerpendicular(point, line)
    return radius >= perpendicularLength 

def solvePerpendicular(point, line):
    # solve the length of the perpendicular segment given a point and a line
    # first, solve the perpendicular function
    x, y = point
    slope1, intercept1 = lineToFunction(line)
    if slope1 == 0: slope1 = 10**(-10)
    slope2 = -1/slope1
    intercept2 = y - slope2 * x
    xi = (intercept2 - intercept1)/(slope1 - slope2)
    yi = slope2 * xi + intercept2
    distance = getDistance(x, y, xi, yi)
    return distance

def linesIntersect(line1, line2):
    # compute the intersect point
    slope1, intercept1 = lineToFunction(line1)
    slope2, intercept2 = lineToFunction(line2)
    # if parallel
    if slope1 == slope2: return False
    # then solve the intersect
    x = (intercept2 - intercept1)/(slope1 - slope2)
    # judge if it is in the range
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    return (min(x1, x2) <= x <= max(x1, x2)) and \
           (min(x3, x4) <= x <= max(x3, x4))

def lineToFunction(line):
    (x1, y1), (x2, y2) = line
    slope = (y1 - y2)/(x1 - x2)
    intercept = y1 - (y1 - y2)/(x1 - x2) * x1
    return slope, intercept


####################################
# Game Class Definition
####################################

class Bird(object):

    def __init__(self, x, y, impulse, angle, data):
        # this __init__ function is inspired by:
        # http://www.pymunk.org/en/latest/pymunk.html#pymunk.Body
        # http://www.pymunk.org/en/latest/pymunk.html#pymunk.Circle
        # http://github.com/estevaofon/angry-birds-python/blob/master
        #        /src/characters.py
        self.mass = 5
        self.radius = 16
        self.moment = pymunk.moment_for_circle(self.mass, 0, self.radius, (0,0))
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = x, data.height - y
        self.angle = angle
        self.impulse = impulse.rotated(self.angle)
        self.body.apply_impulse(self.impulse)
        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.95
        self.currImpulse = self.impulse
        self.disappearing =  False
        self.disappeared = False
        self.disappearTime = 100
        data.space.add(self.body, self.shape)
        self.fallPlayed = False
        self.flyPlayed = False

    def rebound(self, data):
        x, y = self.body.position
        r = self.radius
        for brick in data.bricks:
            left, top, right, bot = brick.getBounds()
            # collide at 8 different regions:
            # collide at left or right
            if (left - r <= x <= left and bot <= y <= top) or \
               (right <= x <= right + r and bot <= y <= top):
                self.currImpulse = Vec2d(-data.coeff * self.currImpulse[0], 
                                          data.coeff * self.currImpulse[1])
                self.body.apply_impulse(self.currImpulse)
            # collide at top or bottom
            if (left <= x <= right and top <= y <= top + r) or \
               (left <= x <= right and bot - r <= y <= bot):
                self.currImpulse = Vec2d(data.coeff * self.currImpulse[0], 
                                        -data.coeff * self.currImpulse[1])
                self.body.apply_impulse(self.currImpulse)
            # collide at top-left corner
            if x <= left and y >= top:
                distance = getDistance(x, y, left, top)
                if distance <= r:
                    self.currImpulse = Vec2d(-data.coeff * self.currImpulse[0], 
                                             -data.coeff * self.currImpulse[1])
                    self.body.apply_impulse(self.currImpulse)
            # collide at top-right corner
            if x >= right and y >= top:
                distance = getDistance(x, y, right, top)
                if distance <= r:
                    self.currImpulse = Vec2d(-data.coeff * self.currImpulse[0], 
                                             -data.coeff * self.currImpulse[1])
                    self.body.apply_impulse(self.currImpulse)
            # collide at left-bot corner
            if x <= left and y <= bot:
                distance = getDistance(x, y, left, bot)
                if distance <= r:
                    self.currImpulse = Vec2d(-data.coeff * self.currImpulse[0], 
                                             -data.coeff * self.currImpulse[1])
                    self.body.apply_impulse(self.currImpulse)
            # collide at right-bot corner
            if x >= right and y <= bot:
                distance = getDistance(x, y, right, bot)
                if distance <= r:
                    self.currImpulse = Vec2d(-data.coeff * self.currImpulse[0], 
                                             -data.coeff * self.currImpulse[1])
                    self.body.apply_impulse(self.currImpulse)

    def draw(self, screen, data):
        phase1, phase2, phase3, step = 100, 70, 40, 20
        screenCoord = getPygameCoords(self.body.position, data)
        x = screenCoord[0] - self.image.get_width()/2
        y = screenCoord[1] - self.image.get_height()/2
        if self.disappearing:
            if self.disappearTime > 0:
                self.disappearTime -= step
            if phase2 <= self.disappearTime < phase1:
                screen.blit(data.phase1, (x, y))
            if phase3 <= self.disappearTime < phase2:
                screen.blit(data.phase2, (x, y))
            if 0 <= self.disappearTime < phase3:
                screen.blit(data.phase3, (x, y))
            if self.disappearTime <= 0:
                self.disappeared = True
        else:
            if self.name in data.paths:
                path = data.paths[self.name]
                if len(path) > 1:
                    x1, y1 = path[-1]
                    x2, y2 = path[-2]
                    if x2 < x1: 
                        angle = math.atan((y2-y1)/(x2-x1))
                        image = self.image
                    elif x1 < x2:
                        angle = math.atan((y2-y1)/(x2-x1))
                        image = pygame.transform.flip(self.image, True, False)
                    else:
                        if y2 < y1: angle = -1/2 * math.pi
                        elif y2 > y1: angle = 1/2 * math.pi
                        else: angle = 0
                        image = self.image
                    angle = radian2degree(angle)
                    image = pygame.transform.rotate(image, angle)
                    screen.blit(image, (x, y))
                else:
                    p0 = (data.x0, data.y0)
                    p1 = (data.x1, data.y1)
                    image = rotateImage(p0, p1, self.image)
                    screen.blit(image, (x, y))

    def sounds(self):
        if self.flyPlayed == False:
            playSounds("sounds/fly.ogg")
            self.flyPlayed = True
        if self.disappearing:
            if self.fallPlayed == False:
                playSounds("sounds/fall.ogg")
                self.fallPlayed = True

class RedBird(Bird):

    def __init__(self, x, y, impulse, angle, data, image):
        super().__init__(x, y, impulse, angle, data)
        self.image = image
        self.cost = 2

class YellowBird(Bird):

    def __init__(self, x, y, impulse, angle, data, image):
        super().__init__(x, y, impulse, angle, data)
        self.image = image
        self.accelerated = False
        self.cost = 3
        self.initImpulse = impulse

    def accelerate(self, accAngle):
        if self.accelerated == False:
            ratio = 1.5
            self.impulse *= ratio
            self.accAngle = math.pi - accAngle
            self.body.apply_impulse(self.initImpulse.rotated(self.accAngle))
            self.accelerated = True

class BlueBird(Bird):

    def __init__(self, x, y, impulse, angle, data, image):
        super().__init__(x, y, impulse, angle, data)
        self.initImpulse = impulse
        self.image = image
        self.tripled = False
        self.cost = 5

    def scatterShot(self, angle, data):
        if self.tripled == False:
            units = 18
            x, y = self.body.position
            upperAngle = math.pi - (angle + math.pi/units)
            lowerAngle = math.pi - (angle - math.pi/units)
            upperBird = BlueBirdCopy(x, y, self.initImpulse, upperAngle, data,
                                     self.image)
            birdID = "bird" + str(data.birdID) + "upperCopy"
            upperBird.name = birdID
            data.objects.append(upperBird)
            lowerBird = BlueBirdCopy(x, y, self.initImpulse, lowerAngle, data,
                                     self.image)
            birdID = "bird" + str(data.birdID) + "lowerCopy"
            lowerBird.name = birdID
            data.objects.append(lowerBird)
            self.tripled = True

class BlueBirdCopy(BlueBird):
    
    def __init__(self, x, y, impulse, angle, data, image):
        super().__init__(x, y, impulse, angle, data, image)
        self.body.position.y = data.height - self.body.position.y
        self.cost = 0
        self.tripled = True

    def sounds(self):
        pass

class GreenBird(Bird):

    def __init__(self, x, y, impulse, angle, data, image):
        super().__init__(x, y, impulse, angle, data)
        self.image = image
        self.cost = 8
        self.callBacked = False

    def callBack(self, data):
        if self.callBacked == False:
            coeff = 20
            x, y = self.body.position
            distance = getDistance(data.launchCx, data.launchCy, x, y)
            dx = data.launchCx - x
            dy = data.launchCy - y
            # adjust impluse
            if distance > coeff:
                distance = coeff
            # apply impulse
            self.currImpulse = Vec2d(dx, dy) * distance - self.currImpulse
            self.body.apply_impulse(self.currImpulse)
            self.callBacked = True

class WhiteBird(Bird):

    def __init__(self, x, y, impulse, angle, data, image):
        super().__init__(x, y, impulse, angle, data)
        self.image = image
        self.cost = 15
        self.exploded = False

    def explode(self, data):
        self.explosionRadius = 300
        x0, y0 = self.body.position
        units = 50
        if self.exploded == False: 
            for target in data.objects:
                if isinstance(target, Pig):
                    x1, y1 = target.body.position
                    distance = getDistance(x0, y0, x1, y1)
                    if (distance <= self.explosionRadius) and \
                       (not existObstacles(data, self, target)):
                        coeff = (self.explosionRadius - distance)
                        impulseUnit = Vec2d((x1 - x0)/units, (y1 - y0)/units)
                        impulse = impulseUnit * coeff
                        target.body.apply_impulse(impulse)
            playSounds("sounds/tnt.ogg")
            self.exploded = True
            self.disappearing = True

    def draw(self, screen, data):
        phase0, phase1, phase2, phase3, step = 100, 80, 60, 40, 20
        screenCoord = getPygameCoords(self.body.position, data)
        x = screenCoord[0] - self.image.get_width()/2
        y = screenCoord[1] - self.image.get_height()/2
        if self.disappearing:
            if self.disappearTime > 0:
                self.disappearTime -= step
            if phase1 <= self.disappearTime < phase0:
                screen.blit(data.phase0, (x, y))
            if phase2 <= self.disappearTime < phase1:
                screen.blit(data.phase1, (x, y))
            if phase3 <= self.disappearTime < phase2:
                screen.blit(data.phase2, (x, y))
            if 0 <= self.disappearTime < phase3:
                screen.blit(data.phase3, (x, y))
            if self.disappearTime <= 0:
                self.disappeared = True
        else:
            super().draw(screen, data) 

class Pig(object):

    def __init__(self, x, y, radius, image, data):
        self.image = image
        self.mass = 1
        self.radius = radius
        self.moment = pymunk.moment_for_circle(self.mass, 0, self.radius, (0,0))
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.95
        self.pts = 15
        self.disappearing =  False
        self.disappeared = False
        self.disappearTime = 100
        data.space.add(self.body, self.shape)
        self.fallPlayed = False

    def draw(self, screen, data):
        phase1, phase2, phase3, step = 100, 70, 40, 20
        screenCoord = getPygameCoords(self.body.position, data)
        x = screenCoord[0] - self.image.get_width()/2
        y = screenCoord[1] - self.image.get_height()/2
        if self.disappearing:
            if self.disappearTime > 0:
                self.disappearTime -= step
            if phase2 <= self.disappearTime < phase1:
                screen.blit(data.phase1, (x, y))
            if phase3 <= self.disappearTime < phase2:
                screen.blit(data.phase2, (x, y))
            if 0 <= self.disappearTime < phase3:
                screen.blit(data.phase3, (x, y))
            if self.disappearTime <= 0:
                self.disappeared = True
        else:
            screen.blit(self.image, (x, y)) 

    def sounds(self):
        if self.disappearing:
            if self.fallPlayed == False:
                playSounds("sounds/fall.ogg")
                self.fallPlayed = True

class Stone(object):

    def __init__(self, x, y, image, data):
        self.image = image
        self.mass = 50
        self.radius = 18
        self.moment = pymunk.moment_for_circle(self.mass, 0, self.radius, (0,0))
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.95
        self.crushed = False
        self.disappearing =  False
        self.disappeared = False
        self.disappearTime = 100
        data.space.add(self.body, self.shape)
        self.fallPlayed = False

    def crush(self, data):
        if not self.crushed:
            x0, y0 = self.body.position
            for target in data.objects:
                if isinstance(target, Pig):
                    x1, y1 = target.body.position
                    distance = getDistance(x0, y0, x1, y1)
                    threshold = self.radius + target.radius
                    if distance <= threshold:
                        target.disappearing = True
                        self.crushed = True
                        self.disappearing = True
                        return

    def draw(self, screen, data):
        phase1, phase2, phase3, step = 100, 70, 40, 20
        screenCoord = getPygameCoords(self.body.position, data)
        x = screenCoord[0] - self.image.get_width()/2
        y = screenCoord[1] - self.image.get_height()/2
        if self.disappearing:
            if self.disappearTime > 0:
                self.disappearTime -= step
            if phase2 <= self.disappearTime < phase1:
                screen.blit(data.phase1, (x, y))
            if phase3 <= self.disappearTime < phase2:
                screen.blit(data.phase2, (x, y))
            if 0 <= self.disappearTime < phase3:
                screen.blit(data.phase3, (x, y))
            if self.disappearTime <= 0:
                self.disappeared = True
        else:
            screen.blit(self.image, (x, y)) 

    def sounds(self):
        if self.disappearing:
            if self.fallPlayed == False:
                playSounds("sounds/fall.ogg")
                self.fallPlayed = True

class Brick(object):

    def __init__(self, x, y, width, height, image, data):
        self.image = image
        self.body = pymunk.Body() 
        self.body.position = (x, y)
        self.left = -width//2
        self.right = width//2
        self.height = height
        self.brick = pymunk.Segment(self.body, (self.left, 0), 
                                   (self.right, 0), self.height) 
        data.space.add(self.brick) 

    def getBounds(self):
        cx, cy = self.body.position
        left, right = cx + self.left, cx + self.right
        top, bot = cy + self.height, cy - self.height
        return left, top, right, bot

    def draw(self, screen, data):
        screenCoord = getPygameCoords(self.body.position, data)
        x = screenCoord[0] - self.image.get_width()/2
        y = screenCoord[1] - self.image.get_height()/2
        screen.blit(self.image, (x, y))   

class vBrick(Brick):

    def __init__(self, x, y, width, height, image, data):
        self.image = image
        self.body = pymunk.Body() 
        self.body.position = (x, y)
        self.top = height//2
        self.bot = -height//2
        self.width = width
        self.brick = pymunk.Segment(self.body, (0, self.top), (0, self.bot), 
                                    self.width) 
        data.space.add(self.brick) 

    def getBounds(self):
        cx, cy = self.body.position
        left, right = cx - self.width, cx + self.width
        top, bot = cy + self.top, cy + self.bot
        return left, top, right, bot

class Seesaw(object):
    # this classed is created by following the pymunk official tutorial:
    # http://www.pymunk.org/en/latest/pymunk.html#pymunk.Segment
    # http://www.pymunk.org/en/latest/tutorials/SlideAndPinJoint.html
    def __init__(self, x, y, width, height, image, data):
        self.mass = 10
        self.moment = 100000
        self.fence = 20
        self.width = width
        self.height = height
        self.limit = 25
        self.distance = 100
        self.centerBody = pymunk.Body()
        self.centerBody.position = (x, y)
        self.limitBody = pymunk.Body() 
        self.limitBody.position = (x - self.distance, y)
        self.mainBody = pymunk.Body(self.mass, self.moment)
        self.mainBody.position = (x, y)
        self.seesaw = pymunk.Segment(self.mainBody, (-self.width//2, 0), 
                                (self.width//2, 0), self.height)
        self.centerBody = pymunk.PinJoint(self.mainBody, self.centerBody, 
                                         (0, 0), (0, 0))
        self.limitBody = pymunk.SlideJoint(self.mainBody, self.limitBody, 
                                (-self.distance, 0), (0, 0), 0, self.limit) 
        data.space.add(self.seesaw, self.mainBody, 
                       self.centerBody, self.limitBody)
        self.image = image

    def draw(self, screen, data):
        angle = radian2degree(self.seesaw.body.angle)
        image = pygame.transform.rotate(self.image, angle)
        x, y = getPygameCoords(self.seesaw.body.position, data)
        x -= image.get_width()//2
        y -= image.get_height()//2
        screen.blit(image, (x, y))

class Wormhole(object):

    def __init__(self, x, y, image, data, hScope=0, vScope=0):
        self.x = x
        self.y = y
        self.dx = 5
        self.dy = 5
        self.image = image
        self.radius = 30
        self.hScope = hScope
        self.vScope = vScope
        self.leftBound = self.x - hScope
        self.rightBound = self.x + hScope
        self.lowerBound = self.y - vScope
        self.upperBound = self.y + vScope
        self.ejecting = False
        self.soundsPlayed = False

    def move(self):
        if self.hScope != 0:
            if self.x <= self.leftBound\
            or self.x >= self.rightBound:
                self.dx *= -1
            self.x += self.dx
        if self.vScope != 0:
            if self.y <= self.lowerBound\
            or self.y >= self.upperBound:
                self.dy *= -1
            self.y += self.dy      

    def link(self, other):
        self.port = other
        other.port = self

    def detect(self, data):
        x0, y0 = self.x, self.y
        for target in data.objects:
            if isinstance(target, Bird):
                if target.name == "bird" + str(data.birdID):
                    x1, y1 = target.body.position
                    distance = getDistance(x0, y0, x1, y1)
                    threshold = self.radius + target.radius 
                    if not self.ejecting:
                        if distance <= threshold:
                            self.port.ejecting = True
                            self.transfer(target, data)
                            self.soundsPlayed = False
                    else:
                        if distance > threshold:
                            self.ejecting = False

    def transfer(self, target, data):
        exit = self.port
        target.body.position = exit.x, exit.y
        if self.soundsPlayed == False:
            playSounds("sounds/wormhole.ogg")
            self.soundsPlayed = True

    def draw(self, screen, data):
        x, y = self.x, data.height - self.y
        x -= self.image.get_width()//2
        y -= self.image.get_height()//2
        screen.blit(self.image, (x, y))

class Blackhole(object):

    def __init__(self, x, y, affectRadius, image, hScope=0, vScope=0):
        self.x = x 
        self.y = y
        self.dx = 5
        self.dy = 5
        self.radius = 20
        self.affectRadius = affectRadius
        self.image = image
        self.activated = True
        self.timeCountDown = 100
        self.hScope = hScope
        self.vScope = vScope
        self.leftBound = self.x - hScope
        self.rightBound = self.x + hScope
        self.lowerBound = self.y - vScope
        self.upperBound = self.y + vScope

    def attract(self, data):
        if self.activated:
            x0, y0 = self.x, self.y
            for target in data.objects:
                x1, y1 = target.body.position
                distance = getDistance(x0, y0, x1, y1)
                if distance <= self.affectRadius:
                    data.objectsToRemove.append(target)

    def activationCountDown(self):
        step = 2
        reset = 100
        if self.timeCountDown != 0:
            self.timeCountDown -= step
        if self.timeCountDown <= 0:
            self.timeCountDown = reset
            self.activated = not self.activated

    def move(self): 
        if self.activated:
            if self.hScope != 0:
                if self.x <= self.leftBound\
                or self.x >= self.rightBound:
                    self.dx *= -1
                self.x += self.dx
            if self.vScope != 0:
                if self.y <= self.lowerBound\
                or self.y >= self.upperBound:
                    self.dy *= -1
                self.y += self.dy 

    def draw(self, screen, data):
        if self.activated:
            x, y = self.x, data.height - self.y
            x -= self.image.get_width()/2
            y -= self.image.get_height()/2
            screen.blit(self.image, (x, y)) 

class Bomb(object):

    def __init__(self, x, y, affectRadius, image):
        self.x = x
        self.y = y
        self.radius = 25
        self.explosionRadius = affectRadius
        self.disappearing = False
        self.triggered = False
        self.disappeared = False
        self.image = image
        self.disappearTime = 100
        self.explodePlayed = False

    def trigger(self, data):
        if not self.triggered:
            for target in data.objects:
                x, y = target.body.position
                distance = getDistance(self.x, self.y, x, y)
                if distance <= self.radius + target.radius:
                    self.triggered = True

    def explode(self, data):
        x0, y0 = self.x, self.y
        units = 60
        if self.triggered:
            if self.explodePlayed == False:
                playSounds("sounds/tnt.ogg")
                self.explodePlayed = True
            for target in data.objects:
                x1, y1 = target.body.position
                distance = getDistance(x0, y0, x1, y1)
                if (distance <= self.explosionRadius) and \
                   (not existObstacles(data, self, target)):
                    coeff = (self.explosionRadius - distance)
                    impulseUnit = Vec2d((x1 - x0)/units, (y1 - y0)/units)
                    impulse = impulseUnit * coeff
                    target.body.apply_impulse(impulse)
            self.disappearing = True

    def draw(self, screen, data):
        phase0, phase1, phase2, phase3, step = 100, 80, 60, 40, 20
        x = self.x - self.image.get_width()/2
        y = data.height - self.y - self.image.get_height()/2
        if self.disappearing:
            if self.disappearTime > 0:
                self.disappearTime -= step
            if phase1 <= self.disappearTime < phase0:
                screen.blit(data.phase0, (x, y))
            if phase2 <= self.disappearTime < phase1:
                screen.blit(data.phase1, (x, y))
            if phase3 <= self.disappearTime < phase2:
                screen.blit(data.phase2, (x, y))
            if 0 <= self.disappearTime < phase3:
                screen.blit(data.phase3, (x, y))
            if self.disappearTime <= 0:
                self.disappeared = True
        else:
            screen.blit(self.image, (x, y)) 

