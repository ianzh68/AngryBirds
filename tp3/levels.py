import pygame
from classes import *


####################################
# Common sharing helper functions
####################################

def getButtonBounds(cx, cy, button):
    left = cx - button.get_width()//2
    right = cx + button.get_width()//2
    top = cy - button.get_height()//2
    bot = cy + button.get_height()//2
    return (left, top, right, bot)


####################################
# Common sharing init functions
####################################

def initGameStatus(data):
    data.end = False
    data.time = 0
    data.launching = False
    data.clicking = False
    data.currBird = "red"
    data.currBirdImage = data.redBird
    data.selectedBird = None
    data.selectedGameButton = None
    data.selectedDialogueButton = None
    data.score = 0
    data.levelCleared = False
    data.launchPlayed = False
    data.completePlayed = False
    if data.mode.startswith("level"):
        data.record = dict()
        data.record["mode"] = data.mode

def initSpace(data):
    # create the space
    data.space = pymunk.Space()
    data.space.gravity = (0, -900)

def initPaths(data):
    # set up path tracking system
    data.paths = dict()
    data.nextRecord = 100
    data.birdID = -1

def initObjects(data):
    # create variables to store/delete birds and pigs
    data.objects = list()
    data.objectsToRemove = list()
    data.blackholes = list()
    data.wormholes = list()
    data.seesaws = list()
    data.bombs = list()
    data.bombsToRemove = list()

def initDialogueButtons(data):
    white, yellow = (255, 255, 255), (255, 255, 0)
    font = pygame.font.Font("Angrybirds-regular.ttf", 26)
    data.chooselevels = font.render("back  ", 1, white)
    data.nextlevel = font.render("  continue  ", 1, white)
    data.playagain = font.render("  retry", 1, white)
    data.highscore = font.render("watch replay", 1, white)
    data.dialogueButtons = [data.chooselevels, data.nextlevel, 
                            data.playagain, data.highscore]
    data.cChooselevels = font.render("BACK  ", 1, yellow)
    data.cNextlevel = font.render("  CONTINUE  ", 1, yellow)
    data.cPlayagain = font.render("  RETRY", 1, yellow)
    data.cHighscore = font.render("WATCH REPLAY", 1, yellow)
    data.cDialogueButton = [data.cChooselevels, data.cNextlevel, 
                            data.cPlayagain, data.cHighscore]
    x, y = data.width//2, 500
    bound1 = getButtonBounds(x, y, data.nextlevel)
    minx = bound1[0] - data.chooselevels.get_width()
    bound0 = (minx, bound1[1], bound1[0], bound1[-1])
    maxx = bound1[2] + data.playagain.get_width()
    bound2 = (bound1[2], bound1[1], maxx, bound1[-1])
    x, y = data.width//2, 600
    bound3 = getButtonBounds(x, y, data.highscore)
    data.dialogueButtonBounds = [bound0, bound1, bound2, bound3]
    if data.mode.endswith("X"):
        data.dialogueButtons = data.dialogueButtons[:-1]
        data.cDialogueButton = data.cDialogueButton[:-1]
        data.dialogueButtonBounds = data.dialogueButtonBounds[:-1]

def initGameButtons(data):
    white, yellow = (255, 255, 255), (255, 255, 0)
    if data.mode.startswith("level"):
        font = pygame.font.Font("Angrybirds-regular.ttf", 26)
        data.back = font.render("back  ", 1, white)
        data.skip = font.render(" skip ", 1, white)
        data.retry = font.render("  retry", 1, white)
        data.gameButtons = [data.back, data.skip, data.retry]    
        data.cBack = font.render("BACK  ", 1, yellow)
        data.cSkip = font.render(" SKIP ", 1, yellow)
        data.cRetry = font.render("  RETRY", 1, yellow)
        data.cGameButton = [data.cBack, data.cSkip, data.cRetry]
        x, y = 40, 640
        data.gameButtonBounds = []
        for i in range(len(data.gameButtons)):
            if i > 0:
                x += data.gameButtons[i-1].get_width()
            left, right = x, x + data.gameButtons[i].get_width()
            top, bot = y, y + data.gameButtons[i].get_height()
            data.gameButtonBounds += [(left, top, right, bot)]

def initBirdButtons(data):
    margin, length = 40, 60
    data.birdImages = [
                       data.redBird2bc, 
                       data.yellowBird2bc, 
                       data.blueBird2bc,
                       data.greenBird2bc, 
                       data.whiteBird2bc
                       ]
    data.chosenBird = [
                       data.redChosen, 
                       data.yellowChosen, 
                       data.blueChosen,
                       data.greenChosen, 
                       data.whiteChosen
                       ]
    x0, y0 = 700, 660
    data.birdBounds = []
    for i in range(len(data.birdImages)):
        x = x0 + i * length
        y = y0
        left, right = x - length//2, x + length//2
        top, bot = y - length//2, y + length//2
        data.birdBounds += [(left, top, right, bot)]

def initLevelsUI(data):
    # birds
    initBirdButtons(data)
    # buttons
    initGameButtons(data)
    initDialogueButtons(data)


####################################
# Level1
####################################

def initLevel1(data):

    # init bricks
    def initBricks(data):
        data.bricks = []
        x, y, width, height = 500, 300, 204, 10
        newBrick = Brick(x, y, width, height, data.hPlatform, data)
        data.bricks.append(newBrick)
        x, y, width, height = 700, 300, 204, 10
        newBrick = Brick(x, y, width, height, data.hPlatform, data)
        data.bricks.append(newBrick)
        data.coeff = 0.2

    # init pigs
    def initPigs(data):
        data.pigs = 18
        pts = 15
        data.goal = data.pigs * pts
        rows, cols = 3, 3
        diameter = 30
        pigCoords = []
        # compute coordinates
        xA, yA = 472, 325
        for row in range(rows):
            for col in range(cols):
                x = xA + col * diameter
                y = yA + row * diameter
                pigCoords.append((x, y))
        xB, yB = 672, 325
        for row in range(rows):
            for col in range(cols):
                x = xB + col * diameter
                y = yB + row * diameter
                pigCoords.append((x, y))
        # create pigs
        for coordinate in pigCoords:
            x, y = coordinate
            newPig = Pig(x, y, diameter//2, data.smallPig, data)
            data.objects.append(newPig)

    def initLaunchArea(data):
        data.launchCx = 150
        data.launchCy = 300
        data.launchRadius = 75

    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)
    initPaths(data)
    initObjects(data)
    initBricks(data)
    initPigs(data)
    initLaunchArea(data)

####################################
# Level2
####################################                    

def initLevel2(data):

    def initBricks(data):
        # compute birck coordinates
        distances = [
                     (-200, +200), (+200, +200),
                     (-350, + 70), (+350, + 70),
                     (-200, - 60), (+200, - 60),
                     (-350, -190), (+350, -190)
                     ]
        brickCoords = []
        for distance in distances:
            hDistance, vDistance = distance
            x, y = data.width//2 + hDistance, data.height//2 + vDistance
            brickCoords += [(x, y)]
        # create bricks
        data.bricks = []
        width, height = 84, 10
        for coordinate in brickCoords:
            x, y = coordinate
            newBrick = Brick(x, y, width, height, data.platform, data)
            data.bricks.append(newBrick)
        # set up rebound coefficient        
        data.coeff = 0.2

    def initPigs(data):
        data.pigs = 20
        pts = 15
        data.goal = data.pigs * pts
        # init large pigs
        largeDiameter = 50
        largePigs = []
        for brick in data.bricks[0:2]:
            x, y = brick.body.position
            height = brick.height
            largePigs += [(x, y + height + largeDiameter//2)]
        for coordinate in largePigs:
            x, y = coordinate
            newPig = Pig(x, y, largeDiameter//2, data.largePig, data)
            data.objects.append(newPig)
        # init small pigs
        rows, cols = 3, 1
        smallDiameter = 30
        smallPigs = []
        for brick in data.bricks[2:]:
            x, y = brick.body.position
            height = brick.height
            x0, y0 = x, y + height + smallDiameter//2
            for row in range(rows):
                for col in range(cols):
                    xi = x
                    yi = y0 + row * smallDiameter
                    smallPigs += [(xi, yi)]
        for coordinate in smallPigs:
            x, y = coordinate
            newPig = Pig(x, y, smallDiameter//2, data.smallPig, data)
            data.objects.append(newPig)

    def initLaunchArea(data):
        data.launchCx = data.width//2
        data.launchCy = data.height//2
        data.launchRadius = 75

    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)
    initPaths(data)
    initObjects(data)
    initBricks(data)
    initPigs(data)
    initLaunchArea(data)

####################################
# Level3
####################################   

def initLevel3(data):

    def initBlackhole(data):
        x, y = 600, 480
        affectRadius = 80
        hScope = 100
        newBlackhole = Blackhole(x, y, affectRadius, data.blackhole, hScope)
        data.blackholes += [newBlackhole]

    def initBricks(data): 
        data.bricks = []
        width, height = 204, 10
        hMargin, vMargin = 250, 80
        hBrickCoords = []
        x, y = 250, data.height//2
        hBrickCoords += [(x, y)]
        x, y = x + width, data.height//2
        hBrickCoords += [(x, y)]
        x, y = data.width - hMargin, data.height - vMargin
        hBrickCoords += [(x, y)]
        x, y = x - width, data.height - vMargin
        hBrickCoords += [(x, y)]
        for coordinate in hBrickCoords:
            x, y = coordinate
            newBrick = Brick(x, y, width, height, data.hPlatform, data)
            data.bricks.append(newBrick)
        vBrickCoords = []
        x, y = 866, y - width//2 - height
        vBrickCoords += [(x, y)]
        x, y = x, y - width
        vBrickCoords += [(x, y)]
        for coordinate in vBrickCoords:
            x, y = coordinate
            newBrick = vBrick(x, y, height, width, data.vPlatform, data)
            data.bricks.append(newBrick)
        data.coeff = 0.5

    def initPigs(data):
        data.pigs = 6
        pts = 15
        data.goal = data.pigs * pts
        rows, cols = 6, 1
        diameter, brickHeight = 30, 10
        pigCoords = []
        x0, y0 = 250, data.height//2 + diameter//2 + brickHeight//2
        for row in range(rows):
            for col in range(cols):
                x = x0
                y = y0 + row * diameter
                pigCoords += [(x, y)]
        for coordinate in pigCoords:
            x, y = coordinate
            newPig = Pig(x, y, diameter//2, data.smallPig, data)
            data.objects.append(newPig)

    def initLaunchArea(data):
        data.launchCx = data.width//2
        data.launchCy = 500
        data.launchRadius = 75

    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)
    initPaths(data)
    initObjects(data)
    initBricks(data)
    initPigs(data)
    initLaunchArea(data)
    initBlackhole(data)

####################################
# Level4
####################################  

def initLevel4(data):

    def initBricks(data): 
        data.bricks = []
        width, height = 204, 10
        hBrickCoords = []
        x, y = 250, 200
        hBrickCoords += [(x, y)]
        x += width
        hBrickCoords += [(x, y)]
        y += width
        hBrickCoords += [(x, y)]
        for coordinate in hBrickCoords:
            x, y = coordinate
            newBrick = Brick(x, y, width, height, data.hPlatform, data)
            data.bricks += [newBrick]
        vBrickCoords = []
        x, y = 158, 312
        vBrickCoords += [(x, y)]
        y += width
        vBrickCoords += [(x, y)]
        for coordinate in vBrickCoords:
            x, y = coordinate
            newBrick = vBrick(x, y, height, width, data.vPlatform, data)
            data.bricks += [newBrick]
        x, y, width, height = 550, 520, 10, 84
        newBrick = vBrick(x, y, width, height, data.shortPlatform, data)
        data.bricks += [newBrick]
        data.coeff = 0.4

    def initPigs(data):
        data.pigs = 15
        pts = 15
        data.goal = data.pigs * pts
        x0, y0 = 425, 430
        rows, cols = 5, 3
        diameter = 30
        pigCoords = []
        for row in range(rows):
            for col in range(cols):
                x = x0 + col * diameter
                y = y0 + row * diameter
                pigCoords += [(x, y)]
        for coordinate in pigCoords:
            x, y = coordinate
            newPig = Pig(x, y, diameter//2, data.smallPig, data)
            data.objects.append(newPig)

    def initWormhole(data):
        x, y, hScope, vScope = 260, 550, 0, 80
        newWormhole = Wormhole(x, y, data.wormhole, data, hScope, vScope)
        data.wormholes += [newWormhole]
        x, y, hScope, vScope = data.width//2, 340, 140, 0
        newWormhole = Wormhole(x, y, data.wormhole, data, hScope, vScope)
        data.wormholes += [newWormhole]
        data.wormholes[0].link(data.wormholes[1])

    def initBombs(data):
        x, y, affectRadius = 375, 438, 200
        newBomb = Bomb(x, y, affectRadius, data.tnt)
        data.bombs.append(newBomb)

    def initLaunchArea(data):
        data.launchCx = 860
        data.launchCy = 320
        data.launchRadius = 75

    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)
    initPaths(data)
    initObjects(data)
    initBricks(data)
    initPigs(data)
    initLaunchArea(data)
    initWormhole(data)
    initBombs(data)

####################################
# Level5
####################################  

def initLevel5(data):

    def initBombs(data):
        x, y, affectRadius = 510, 215, 300
        newBomb = Bomb(x, y, affectRadius, data.tnt)
        data.bombs.append(newBomb)

    def initBricks(data): 
        data.bricks = []
        width, height = 204, 10
        hBrickCoords = []
        x, y = 600, 180
        hBrickCoords += [(x, y)]
        x += width
        hBrickCoords += [(x, y)]
        for coordinate in hBrickCoords:
            x, y = coordinate
            newBrick = Brick(x, y, width, height, data.hPlatform, data)
            data.bricks += [newBrick]
        x, y, distance = 412, 292, 50
        vBrickCoords = []
        vBrickCoords += [(x, y)]
        y += width + distance
        vBrickCoords += [(x, y)]
        x, y = 600, 315
        vBrickCoords += [(x, y)]
        for coordinate in vBrickCoords:
            x, y = coordinate
            newBrick = vBrick(x, y, height, width, data.vPlatform, data)
            data.bricks += [newBrick]
        data.coeff = 0.2
        x, y, radius = 412, 414, 20
        newStone = Stone(x, y, data.stone, data)
        data.objects.append(newStone)

    def initPigs(data):
        data.pigs = 12
        pts = 15
        data.goal = data.pigs * pts
        rows, cols = 3, 4
        x0, y0 = 720, 205
        diameter = 30
        pigCoords = []
        for row in range(rows):
            for col in range(cols):
                x = x0 + col * diameter
                y = y0 + row * diameter
                pigCoords += [(x, y)]
        for coordinate in pigCoords:
            x, y = coordinate
            newPig = Pig(x, y, diameter//2, data.smallPig, data)
            data.objects.append(newPig)

    def initBlackhole(data):
        x, y, hScope, vScope, affectRadius = data.width//2, 450, 0, 80, 80    
        newBlackhole = Blackhole(x, y, affectRadius, data.blackhole, 
                                 hScope, vScope)
        data.blackholes += [newBlackhole]

    def initLaunchArea(data):
        data.launchCx = 200
        data.launchCy = 400
        data.launchRadius = 75

    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)
    initPaths(data)
    initObjects(data)
    initBricks(data)
    initPigs(data)
    initLaunchArea(data)
    initBombs(data)
    initBlackhole(data)

####################################
# Level6
####################################  

def initLevel6(data):
 
    def initBombs(data):
        x, y, affectRadius = 193, 235, 200
        newBomb = Bomb(x, y, affectRadius, data.tnt)
        data.bombs.append(newBomb)

    def initBricks(data): 
        data.bricks = []
        width, height = 204, 10
        hBrickCoords = []
        x, y = 250, 200
        hBrickCoords += [(x, y)]
        x += width
        hBrickCoords += [(x, y)]
        for coordinate in hBrickCoords:
            x, y = coordinate
            newBrick = Brick(x, y, width, height, data.hPlatform, data)
            data.bricks += [newBrick]
        vBrickCoords = []
        x, y = 158, 312
        vBrickCoords += [(x, y)]
        y += width
        vBrickCoords += [(x, y)]
        for coordinate in vBrickCoords:
            x, y = coordinate
            newBrick = vBrick(x, y, height, width, data.vPlatform, data)
            data.bricks += [newBrick]
        data.coeff = 0.3

    def initPigs(data):
        data.pigs = 12
        pts = 15
        data.goal = data.pigs * pts
        x0, y0 = 322, 225
        rows, cols = 4, 3
        diameter = 30
        pigCoords = []
        for row in range(rows):
            for col in range(cols):
                x = x0 + col * diameter
                y = y0 + row * diameter
                pigCoords += [(x, y)]
        for coordinate in pigCoords:
            x, y = coordinate
            newPig = Pig(x, y, diameter//2, data.smallPig, data)
            data.objects.append(newPig)

    def initSeesaw(data):
        x, y = data.width//2, data.height//2
        width, height = 204, 10
        newSeesaw = Seesaw(x, y, width, height, data.seesaw, data)
        data.seesaws += [newSeesaw]

    def initWormhole(data):
        x, y, hScope, vScope = 270, 370, 60, 0
        newWormhole = Wormhole(x, y, data.wormhole, data, hScope, vScope)
        data.wormholes += [newWormhole]
        x, y, hScope, vScope = 660, 230, 0, 110
        newWormhole = Wormhole(x, y, data.wormhole, data, hScope, vScope)
        data.wormholes += [newWormhole]
        data.wormholes[0].link(data.wormholes[1])   

    def initBlackhole(data):
        x, y, hScope, vScope, affectRadius = 530, 500, 60, 60, 80    
        newBlackhole = Blackhole(x, y, affectRadius, data.blackhole, 
                                 hScope, vScope)
        data.blackholes += [newBlackhole]

    def initStone(data):
        x, y = 250, 228
        newStone = Stone(x, y, data.stone, data)
        data.objects += [newStone]

    def initLaunchArea(data):
        data.launchCx = 800
        data.launchCy = 200
        data.launchRadius = 75

    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)
    initPaths(data)
    initObjects(data)
    initBricks(data)
    initPigs(data)
    initLaunchArea(data)
    initBombs(data)
    initSeesaw(data)
    initWormhole(data)
    initBlackhole(data)
    initStone(data)
