import pygame
import time
import os
import math
from pygame.locals import *
from pygame.color import *
from buttons import *
from classes import *
from levels import *


# source of font "Angrybirds-regular.ttf" used in this entire project:
# http://www.daimg.com/font/201307/ziti_33438.html


####################################
# Common sharing helper functions
####################################

def listFiles(path):
    files = []
    for filename in os.listdir(path):
        if filename.endswith(".TXT"):
            files += [filename]
    return files

def readFile(path):
    # this function is from 15-112 class note:
    # http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    # this function is from 15-112 class note:
    # http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
    with open(path, "wt") as f:
        f.write(contents)

def sortDict(dictionary):
    result = []
    for key in dictionary:
        result.append([key, dictionary[key]])
    result.sort()
    return result

def getCurrentTime():
    currTime = time.localtime(time.time())
    currTime = time.strftime('%Y-%m-%d %H:%M:%S', currTime)
    return currTime

def clickInNamedZone(click, zone):
    x, y = click
    left = zone[0][0]
    top = zone[0][1]
    right = zone[-1][-2]
    bot = zone[0][-1]
    return left <= x <= right and top <= y <= bot

def clickOnButton(button, click):
    x, y = click
    if isinstance(button, CircleButton):
        distance = getDistance(button.cx, button.cy, x, y)
        return distance <= button.radius
    elif isinstance(button, RectButton):
        left, top, right, bot = button.bounds
        return left <= x <= right and top <= y <= bot

def removeobjects(data):
    ground = 85    
    for target in data.objects:
        if target.body.position.y <= ground:
            target.body.position.y = ground
            target.disappearing = True
    for target in data.objects:
        if target.disappeared:
            data.objectsToRemove.append(target) 
    for target in data.objectsToRemove:
        if isinstance(target, Pig):
            data.pigs -= 1 
            data.score += target.pts
        data.space.remove(target.body)
        data.space.remove(target.shape)
        data.objects.remove(target)
    data.objectsToRemove = list()
    for target in data.bombs:
        if target.disappeared:
            data.bombsToRemove.append(target)
    for target in data.bombsToRemove:
        data.bombs.remove(target)
    data.bombsToRemove = list()

def getNewestBirdAngle(data):
    birdID = data.birdID
    birdName = "bird" + str(birdID)
    birdPath = data.paths[birdName]
    if len(birdPath) >= 2:
        x0, y0 = birdPath[-2]
        x1, y1 = birdPath[-1]
        if x1 < x0: angle = math.atan((y1 - y0)/(x0 - x1))
        elif x1 > x0: angle = math.pi - math.atan((y1 - y0)/(x1 - x0))
        else:
            if y1 < y0: angle = -1/2 * math.pi 
            elif y1 > y0: angle = 1/2 * math.pi
            else: angle = 0
        data.newestBirdAngle = angle
    else:
        data.newestBirdAngle = None

def getFlyPath(data, target):
    birdID = target.name
    if data.nextRecord != 0:
        data.nextRecord -= 50
    if data.nextRecord == 0:
        x, y = target.body.position
        if birdID in data.paths:
            data.paths[birdID].append((x, y))
        else:
            data.paths[birdID] = [(x, y)]
        data.nextRecord == 100

def clickInLaunchZone(data, click):
    x, y = click
    distance = getDistance(x, y, data.launchCx, data.launchCy)
    return data.launchRadius >= distance

def saveScore(data):
    if data.mode.startswith("level"):
        if not data.mode.endswith("X"):
            level = data.mode
            score = data.score
            goal = data.goal
            try:
                scoreRecords = readFile("score.txt")
                if scoreRecords == "":
                    scoreRecords = dict()
                else:
                    scoreRecords = eval(scoreRecords)
                if level in scoreRecords:
                    for key in scoreRecords:
                        if key == level:
                            if scoreRecords[key] < score:
                                scoreRecords[key] = str(score)+" / "+str(goal)
                else: 
                    scoreRecords[level] = str(score)+" / "+str(goal)
                writeFile("score.txt", str(scoreRecords))
            except:
                scoreRecords = dict()
                scoreRecords[level] = str(score)+" / "+str(goal)
                writeFile("score.txt", str(scoreRecords))


####################################
# Common sharing event functions
####################################

def levelsMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            # choosing birds
            chooseBird(data, event)
            # choosing buttons
            chooseGameButton(data, event)
            chooseDialogueButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            # launch the bird
            launchBird(data, event)
            # button response
            gameButtonResponse(data, event)
            dialogueButtonResponse(data, event)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            # release the bird 
            releaseBird(data, event)

def levelsKeyPressed(data, events):
    for event in events:
        if not data.levelCleared: 
            if event.type == KEYDOWN:
                # quit the game
                if event.key == K_ESCAPE:
                    data.playing = False
                # use birds' abilities
                if event.key == K_SPACE:
                    useBirdAbilities(data)

def launchBird(data, event):
    if not data.levelCleared:
        if clickInLaunchZone(data, event.pos):
            data.x0, data.y0 = event.pos
            data.launching = True
            data.record[data.time] = ["launch", data.currBird, data.x0, data.y0]
        if clickInNamedZone(event.pos, data.birdBounds):
            length, left = 60, 670
            x, y = event.pos
            birdIndex = (x - left)//length
            if birdIndex == 0: data.currBird = "red"
            if birdIndex == 1: data.currBird = "yellow"
            if birdIndex == 2: data.currBird = "blue"
            if birdIndex == 3: data.currBird = "green"
            if birdIndex == 4: data.currBird = "white"
            data.currBirdImage = eval("data." + data.currBird + "Bird")
            data.record[data.time] = ["select", data.currBird]

def chooseBird(data, event):
    if not data.levelCleared:
        if clickInNamedZone(event.pos, data.birdBounds):
            length, left = 60, 670
            x, y = event.pos
            data.birdIndex = (x - left)//length
            if data.birdIndex < len(data.chosenBird):
                data.selectedBird = data.chosenBird[data.birdIndex]
        else: data.selectedBird = None

def chooseGameButton(data, event):
    if not data.levelCleared:
        if clickInNamedZone(event.pos, data.gameButtonBounds):
            x, y = event.pos
            for i in range(len(data.gameButtonBounds)):
                left, top, right, bot = data.gameButtonBounds[i]
                if left <= x <= right and top <= y <= bot:
                    data.selectedGameButton = i
        else: data.selectedGameButton = None

def chooseDialogueButton(data, event):
    if data.levelCleared:
        if clickInNamedZone(event.pos, data.dialogueButtonBounds[:-1]) or \
           clickInNamedZone(event.pos, data.dialogueButtonBounds[-1:]):
            x, y = event.pos
            for i in range(len(data.dialogueButtonBounds)):
                left, top, right, bot = data.dialogueButtonBounds[i]
                if left <= x <= right and top <= y <= bot:
                    data.selectedDialogueButton = i
        else: data.selectedDialogueButton = None

def gameButtonResponse(data, event):
    if data.selectedGameButton == 0:
        # back
        if data.mode.endswith("X"):
            data.mode = "editor"
            initEditor(data)
        else:
            data.mode = "submenu"
            initSubmenu(data)
    elif data.selectedGameButton == 1:
        # skip
        if data.mode.endswith("X"):
            data.mode = "editor"
            initEditor(data)
        else:
            totalLevels = 6
            nextLevel = int(data.mode[-1])
            if nextLevel < totalLevels: 
                nextLevel += 1
                data.mode = "level" + str(nextLevel)
                funcName = "initLevel" + str(nextLevel) + "(data)"
                eval(funcName)
    elif data.selectedGameButton == 2:
        # retry
        if data.mode.endswith("X"):
            initLevelX(data)
        else:
            currLevel = data.mode[-1]
            funcName = "initLevel" + currLevel + "(data)"
            eval(funcName)

def dialogueButtonResponse(data, event):
    replayButton = 3
    if data.levelCleared:
        if data.selectedDialogueButton == 0:
            # back
            if data.mode.endswith("X"):
                data.mode = "editor"
                initEditor(data)
            else:
                data.mode = "submenu"
                initSubmenu(data)
        elif data.selectedDialogueButton == 1:
            # continue
            if data.mode.endswith("X"):
                data.mode = "editor"
                initEditor(data)                
            else:
                totalLevels = 6
                nextLevel = int(data.mode[-1])
                if nextLevel < totalLevels: 
                    nextLevel += 1
                    data.mode = "level" + str(nextLevel)
                    funcName = "initLevel" + str(nextLevel) + "(data)"
                    eval(funcName)
        elif data.selectedDialogueButton == 2:
            # retry
            currLevel = data.mode[-1]
            funcName = "initLevel" + currLevel + "(data)"
            eval(funcName)
        elif data.selectedDialogueButton == replayButton:
            if not data.mode.endswith("X"):
                currTime = getCurrentTime()
                filename = "videos/NEW VIDEO MADE AT " + currTime + ".TXT"
                writeFile(filename, str(data.record))
                data.mode = "replay"
                initReplay(data)
                data.prevMode = "level"
            
def releaseBird(data, event):
    if data.launching:
        data.x1, data.y1 = event.pos
        distance = getDistance(data.x1, data.y1, data.x0, data.y0)
        impulse = getImpulse(distance, data)
        angle = getLaunchAngle(data)
        className = data.currBird[0].upper() + data.currBird[1:] + "Bird"
        inputName = "(data.x0, data.y0, impulse, angle, data, "
        imageName = "data." + data.currBird + "Bird"
        funcName = className + inputName + imageName + ")"
        data.record[data.time] = ["release", funcName, impulse, angle, 
                                  data.x1, data.y1]
        newBird = eval(funcName)  
        data.launchPlayed = False     
        data.birdID += 1
        newBird.name = "bird" + str(data.birdID)
        data.score -= newBird.cost
        data.launching = False
        data.objects.append(newBird)

def useBirdAbilities(data):
    if not data.launching:
        birdID = "bird" + str(data.birdID)
        for target in data.objects:
            if type(target) == RedBird: pass
            if type(target) == YellowBird:
                if target.name == birdID:
                    getNewestBirdAngle(data)
                    accAngle = data.newestBirdAngle
                    target.accelerate(accAngle)
                    data.record[data.time] = ["ability", data.currBird]
            if type(target) == BlueBird:
                if target.name == birdID:
                    getNewestBirdAngle(data)
                    angle = data.newestBirdAngle
                    target.scatterShot(angle, data)
                    data.record[data.time] = ["ability", data.currBird]
            if type(target) == WhiteBird:
                if target.name == birdID:
                    target.explode(data)
                    data.record[data.time] = ["ability", data.currBird]
            if type(target) == GreenBird:
                if target.name == birdID:
                    getNewestBirdAngle(data)
                    angle = data.newestBirdAngle
                    target.callBack(data)
                    data.record[data.time] = ["ability", data.currBird]


####################################
# Common sharing draw functions
####################################

def levelsRedrawAll(data, screen):
    # draw background
    screen.blit(data.background, (0,0))
    # draw launch zone
    x = data.launchCx - data.launchRadius
    y = data.launchCy - data.launchRadius
    screen.blit(data.launchZone, (x, y))
    # draw bird selection
    if data.mode.startswith("level"):
        drawBirdSelection(data, screen)
    # draw button selection
    if data.mode.startswith("level"):
        drawButtonSelection(data, screen)
    # draw score
    drawScores(data, screen)
    # draw bird paths, if any:
    drawBirdPath(data, screen)
    # draw objects
    drawObjects(data, screen)
    # draw launch
    drawLaunch(data, screen)
    # draw upgrade 
    if data.levelCleared:
        if data.mode.startswith("level"):
            drawLevelCleared(data, screen)

def drawBirdSelection(data, screen):
    margin, length, fontsize, fontcolor = 40, 60, 30, (255, 255, 255)
    x0, y0 = 700, 660
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    text = font.render("Choose Your Bird:       ", 1, fontcolor)
    x, y = x0 - text.get_width(), y0 - text.get_height()//2
    screen.blit(text, (x, y))
    for i in range(len(data.birdBounds)):
        x, y = x0 + i * length, y0
        drawTemp(screen, x, y, data.birdImages[i])
    if data.selectedBird != None:
        x, y = x0 + data.birdIndex * length, y0
        drawTemp(screen, x, y, data.selectedBird)
    birdcolor = ["red", "yellow", "blue", "green", "white"]
    index = birdcolor.index(data.currBird)
    left, top, right, bot = data.birdBounds[index]
    x = right - data.current.get_width()
    y = bot - data.current.get_height()
    screen.blit(data.current, (x, y))

def drawButtonSelection(data, screen):
    for i in range(len(data.gameButtonBounds)):
        if data.selectedGameButton != i:
            left, top, right, bot = data.gameButtonBounds[i]
            screen.blit(data.gameButtons[i], (left, top))
    if data.selectedGameButton != None:
        left, top, right, bot = data.gameButtonBounds[data.selectedGameButton]
        screen.blit(data.cGameButton[data.selectedGameButton], (left, top))

def drawScores(data, screen):
    fontsize, fontcolor = 26, (0, 0, 0)
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    x, y = data.width//2, 30
    text = font.render("SCORE: %d" % data.score, 1, fontcolor)
    x -= text.get_width()//2
    y -= text.get_height()//2
    screen.blit(text, (x, y))

def drawLevelCleared(data, screen):
    # play complete music
    if data.completePlayed == False:
        playSounds("sounds/complete.ogg")
        data.completePlayed = True
    # draw background
    alpha = 160
    canvas = (1024, 700)
    black = pygame.Surface(canvas)
    color = (0, 0, 0)
    black.fill(color)
    black.set_alpha(alpha)
    screen.blit(black, (0, 0))
    fontsize, fontcolor = 46, (255, 255, 255)
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    text = font.render("level cleared", 1, fontcolor)
    x, y = data.width//2 - text.get_width()//2, 100
    screen.blit(text, (x, y))
    # draw buttons
    for i in range(len(data.dialogueButtonBounds)):
        if data.selectedDialogueButton != i:
            left, top, right, bot = data.dialogueButtonBounds[i]
            screen.blit(data.dialogueButtons[i], (left, top))
    if data.selectedDialogueButton != None:
        x, y = data.dialogueButtonBounds[data.selectedDialogueButton][:2]
        screen.blit(data.cDialogueButton[data.selectedDialogueButton], (x, y))
    # draw stars
    drawStars(screen, data)

def drawBirdPath(data, screen):
    if len(data.paths) > 0:
        for bird in data.paths:
            if bird.startswith("bird" + str(data.birdID)):
                for dot in data.paths[bird]:
                    x, y = dot
                    x = int(x)
                    y = data.height - int(y)
                    white, radius = (255, 255, 255), 2
                    pygame.draw.circle(screen, white, (x, y), radius)

def drawObjects(data, screen):
    # draw wormholes, if any:
    if len(data.wormholes) > 0:
        for wormhole in data.wormholes:
            wormhole.draw(screen, data)
    # draw blackholes, if any:
    if len(data.blackholes) > 0:
        for blackhole in data.blackholes:
            blackhole.draw(screen, data) 
    # draw bombs, if any:
    if len(data.bombs) > 0:
        for bomb in data.bombs:
            bomb.draw(screen, data)   
    # draw seesaws, if any:
    if len(data.seesaws) > 0:
        for seesaw in data.seesaws:
            seesaw.draw(screen, data)
    # draw birds and pigs
    for target in data.objects:
        target.draw(screen, data)
    # draw bricks
    for brick in data.bricks:
        brick.draw(screen, data)

def drawLaunch(data, screen):
    if data.launching:
        if data.launchPlayed == False:
            playSounds("sounds/sling.ogg")
            data.launchPlayed = True
        if data.mode.startswith("level"):
            x, y = pygame.mouse.get_pos()
            width = 10
            pygame.draw.line(screen, THECOLORS["red"], 
                            (data.x0, data.y0), (x, y), width)
            image = rotateImage((data.x0, data.y0), (x, y), data.currBirdImage)
            drawTemp(screen, data.x0, data.y0, image)

def drawStars(screen, data):
    grade1, grade2, grade3 = 0.2, 0.6, 0.85
    x, y = 273, 190
    if grade1 <= data.grade < grade2:
        screen.blit(data.star1, (x, y))
    elif grade2 <= data.grade < grade3:
        screen.blit(data.star2, (x, y))
    elif grade3 <= data.grade:
        screen.blit(data.star3, (x, y))   


####################################
# Common sharing time functions
####################################

def levelsTimerFired(data):
    # recording:
    data.time += 1
    # refreshing:
    data.space.step(1/data.fps)
    # track the path of each bird
    for target in data.objects:
        if isinstance(target, Bird):
            target.rebound(data)
            getFlyPath(data, target)
        try: target.sounds()
        except: pass
    # wormholes, if any:
    if len(data.wormholes) > 0:
        for wormhole in data.wormholes:
            wormhole.move()
            wormhole.detect(data)
    # blackholes, if any:
    if len(data.blackholes) > 0:
        for blackhole in data.blackholes:
            blackhole.move()
            blackhole.activationCountDown()
            blackhole.attract(data)
    # bombs, if any:
    if len(data.bombs) > 0:
        for bomb in data.bombs:
            bomb.trigger(data)
            bomb.explode(data)
    # remove the objects that are out of the screen
    removeobjects(data)
    if data.mode.startswith("level"):
        if data.pigs == 0:
            data.levelCleared = True
            if data.end == False:
                data.grade = data.score/data.goal
                saveScore(data)
                data.record[data.time] = ["end"]
                data.end = True


####################################
# Replay mode
####################################

def initReplay(data):
    level = data.record["mode"][-1]
    funcName = "initLevel" + level + "(data)"
    if level != "X": 
        eval(funcName)
        data.duration = 0
        for time in data.record:
            if time != "mode":
                if time > data.duration:
                    data.duration = time
        # init buttons
        initReplayButtons(data)
        data.completePlayed = False

def initReplayButtons(data):
    # when replaying
    data.replayButtons = []
    x, y = 50, 650
    newButton = TextButton(x, y, "back")
    data.replayButtons += [newButton]
    x, y = 130, 650
    newButton = TextButton(x, y, "replay")
    data.replayButtons += [newButton]
    # when finished
    data.replayDoneButtons = []
    x, y = 460, 520
    newButton = TextButton(x, y, "back")
    data.replayDoneButtons += [newButton]
    x, y = 564, 520
    newButton = TextButton(x, y, "replay")
    data.replayDoneButtons += [newButton]

def replayMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):    
            chooseReplayButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            replayButtonResponse(data, event)

def chooseReplayButton(data, event):
    if data.time <= data.duration:
        for button in data.replayButtons:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False
    else:
        for button in data.replayDoneButtons:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False    

def replayButtonResponse(data, event):
    if data.time <= data.duration:
        for button in data.replayButtons:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)
    else:
        for button in data.replayDoneButtons:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)    

def replayKeyPressed(data, events):
    # do nothing
    pass

def replayTimerFired(data):
    if data.time <= data.duration:
        levelsTimerFired(data)
        readTimeline(data)

def readTimeline(data):
    for time in data.record:
        if time != "mode":
            if data.time == time:
                action = data.record[time]
                if action[0] == "launch":
                    data.launching = True
                    data.currBird, data.x0, data.y0 = action[1:]
                elif action[0] == "release":
                    funcName, impulse, angle, data.x1, data.y1 = action[1:]
                    newBird = eval(funcName)
                    data.birdID += 1
                    newBird.name = "bird" + str(data.birdID)
                    data.score -= newBird.cost
                    data.launching = False
                    data.objects.append(newBird)
                elif action[0] == "ability":
                    data.currBird = action[1]
                    useBirdAbilities(data)
                elif action[0] == "select":
                    data.currBird = action[1]

def replayRedrawAll(data, screen):
    levelsRedrawAll(data, screen)
    height = 80
    fontsize, fontcolor = 24, (0, 0, 0)
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    if data.time <= data.duration:
        percentage = 100
        progress = round((data.time/data.duration)*percentage)
        text = font.render("REPLAYING...%d%%" % progress, 1, fontcolor)
        x, y = data.width//2 - text.get_width()//2, height
        screen.blit(text, (x, y))
        data.grade = data.score/data.goal
    for button in data.replayButtons:
        button.draw(screen, data)
    if data.time > data.duration:
        alpha = 160
        canvas = (1024, 700)
        black = pygame.Surface(canvas)
        color = (0, 0, 0)
        black.fill(color)
        black.set_alpha(alpha)
        screen.blit(black, (0, 0))
        fontsize, fontcolor = 46, (255, 255, 255)
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
        text = font.render("replay finished", 1, fontcolor)
        x, y = data.width//2 - text.get_width()//2, height
        screen.blit(text, (x, y))
        x, y = data.width//2 - text.get_width()//2, height
        for button in data.replayDoneButtons:
            button.draw(screen, data)
        # draw stars
        drawStars(screen, data) 
        # play sound
        if data.completePlayed == False:
            playSounds("sounds/complete.ogg")
            data.completePlayed = True     


####################################
# Editor mode
####################################

def initEditor(data):
    initToolBar(data)
    data.currItem = None
    data.autoAlign = False
    data.itemID = None
    data.dragging = False
    data.rotate = False
    data.createNew = False
    data.placements = list()
    data.editHistory = list()
    data.currPage = -1
    data.contents = ""
    data.topbound = 50
    data.botbound = 615
    data.undoCount = 0
    data.redoCount = 0
    data.pigCount = 0
    data.wormholeCount = 0
    data.launchZonesCount = 0
    data.error = None
    data.selectScenes = False
    data.showInstruction = False
    data.fileSaved = False

def editorMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            chooseEditorButton(data, event)
            chooseScenesButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            editorButtonResponse(data, event)
            sceneButtonResponse(data, event)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            placeItem(data, event)

def editorKeyPressed(data, events):
    for event in events:
        if event.type == KEYDOWN:
            rotateBricks(data, event)

def editorTimerFired(data):
    # do nothing
    pass

def editorRedrawAll(data, screen):
    screen.blit(data.background, (0,0))
    drawToolBar(screen, data)
    drawEditorButtons(screen, data)
    drawPlacements(screen, data)
    drawDragging(screen, data)
    drawPlayError(screen, data)
    drawSceneSelection(screen, data)
    drawSave(screen, data)
    drawEditorInstruction(screen, data)

def rotateBricks(data, event):
    if event.key == K_SPACE:
        if data.dragging:
            if data.currItem == "Long Brick" or \
               data.currItem == "Short Brick":
                    data.rotate = not data.rotate

def drawDragging(screen, data):
    if data.dragging:
        if data.rotate:
            if data.currItem == "Long Brick":
                image = data.vPlatform
            elif data.currItem == "Short Brick":
                image = data.broder
        else:
            index = data.names.index(data.currItem)
            image = data.reals[index]
        x, y = pygame.mouse.get_pos()
        x -= image.get_width()//2
        y -= image.get_height()//2
        screen.blit(image, (x, y))

def drawEditorButtons(screen, data):
    for button in data.editorButtons:
        button.draw(screen, data)
    for button in data.editorIcons:
        button.draw(screen, data)

def drawPlacements(screen, data):
    if data.editHistory != []:
        try:
            data.placements = data.editHistory[data.currPage][:]
            for item in data.placements:
                item.draw(screen, data)
        except:
            drawWarnings(screen, data)
    if data.redoCount >= data.undoCount != 0:
        drawWarnings(screen, data)

def drawWarnings(screen, data):
    fontsize, fontcolor = 26, (0, 0, 0)
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    text = font.render("no more steps available!", 1, fontcolor)
    x = data.width//2 - text.get_width()//2
    y = data.topbound + text.get_height()//2
    screen.blit(text, (x, y))

def drawPlayError(screen, data):
    if data.error != None:
        x, y = data.width//2, (data.topbound + data.botbound)//2
        x -= data.error.get_width()//2
        y -= data.error.get_height()//2
        screen.blit(data.error, (x, y))

def drawSave(screen, data):
    if data.fileSaved:
        fontsize, fontcolor = 26, (0, 0, 0)
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
        text = font.render("file saved successfully!", 1, fontcolor)
        x = data.width//2 - text.get_width()//2
        y = data.topbound + text.get_height()*2
        screen.blit(text, (x, y))      

def drawSceneSelection(screen, data):
    if data.selectScenes:
        # draw background:
        alpha = 160
        canvas = (1024, 700)
        black = pygame.Surface(canvas)
        color = (0, 0, 0)
        black.fill(color)
        black.set_alpha(alpha)
        screen.blit(black, (0, 0))  
        # draw title:
        fontsize, fontcolor, margin = 36, (255, 255, 255), 50
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
        text = font.render("scenes", 1, fontcolor)
        x, y = data.width//2, data.topbound + margin
        x -= text.get_width()//2
        y -= text.get_height()//2
        screen.blit(text, (x, y))
        fontsize = 22
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
        text = font.render("(click 'back' or 'load' agian to quit this page)",
                           1, fontcolor)
        x, y = data.width//2-text.get_width()//2, 130
        screen.blit(text, (x, y))
        # draw record button:
        for button in data.scenebuttons:
            button.draw(screen, data)

def drawToolBar(screen, data):
    alpha = 160
    # draw top bar
    topBar = (1025, 50)
    black = pygame.Surface(topBar)
    color = (0, 0, 0)
    black.fill(color)
    black.set_alpha(alpha)
    screen.blit(black, (0, 0))
    # draw bot bar
    botBar = (1024, 60)
    white = pygame.Surface(botBar)
    color = (255, 255, 255)
    white.fill(color)
    white.set_alpha(alpha)
    bot = 640
    screen.blit(white, (0, bot))

def drawEditorInstruction(screen, data):
    if data.showInstruction:
        # draw background:
        alpha = 160
        canvas = (1024, 700)
        black = pygame.Surface(canvas)
        color = (0, 0, 0)
        black.fill(color)
        black.set_alpha(alpha)
        screen.blit(black, (0, 0))  
        # draw title:
        fontsize, fontcolor, margin = 36, (255, 255, 255), 50
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
        text = font.render("instruction", 1, fontcolor)
        x, y = data.width//2, data.topbound + margin
        x -= text.get_width()//2
        y -= text.get_height()//2
        screen.blit(text, (x, y))
        # draw text:
        fontsize, fontcolor = 22, (255, 255, 255)
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)         
        t = "(click 'BACK' or 'INSTRUCTION' again to quit the instruction page)"
        text = font.render(t, 1, (fontcolor))
        x, y = data.width//2 - text.get_width()//2, 135
        screen.blit(text, (x, y))
        fontsize, fontcolor, margin, distance = 24, (255, 255, 255), 100, 50
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize) 
        x, y = 55, data.topbound + margin
        texts = [
                 "1. drag items at the toolbar at bottom into the " +
                     "screen, place them as whatever you like;", 
                 "2. items cannot overlap with each others;",
                 "3. to start the game, you need exact 1 launch "+
                     "zone and at least 1 pig;",
                 "4. the quantity of wormholes must be even, they work "+
                     "in pairs;",
                 "5. when placing long or short bricks, you can "+
                     "rotate them by pressing 'SPACE';", 
                 "6. 'AUTO-ALIGN' helps align pigs, bricks, tnts "+
                     "and stones if you place them in rows or columns;", 
                 "7. everything except the piglet and the stone is allowed "+
                     "to be floating up in air;",
                 "8. have fun!!!"
                ]
        for i in range(len(texts)):
            y += distance
            text = font.render(texts[i], 1, fontcolor)
            screen.blit(text, (x, y))

def initToolBar(data):
    # initToolBarImages(data)
    initToolBarIcons(data)
    initToolBarButtons(data)

def initToolBarButtons(data):
    data.editorButtons = []
    fontsize, fontcolor = 24, (0, 0, 0)
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    buttons = [
               "back", 
               "clear", 
               "save", 
               "load", 
               "undo", 
               "redo", 
               "play",
               "instruction", 
               "auto-align"
               ]
    x, y, distance = 75, 25, 45
    for i in range(len(buttons)):
        if i > 0:
            width1 = font.render(buttons[i-1], 1, fontcolor).get_width()//2
            width2 = font.render(buttons[i], 1, fontcolor).get_width()//2
            x += width1 + width2 + distance
        if buttons[i] == "instruction" or \
           buttons[i] == "auto-align" or \
           buttons[i] == "load":
            newButton = StatusButton(x, y, buttons[i])
        else:
            newButton = ToolBarButton(x, y, buttons[i])
        data.editorButtons += [newButton]

def initToolBarIcons(data):
    data.editorIcons = []
    data.reals = [
                  data.launchZone, 
                  data.hPlatform, 
                  data.shortBrick, 
                  data.stone, 
                  data.smallPig, 
                  data.tnt, 
                  data.blackhole, 
                  data.wormhole, 
                  data.seesaw
                  ]
    data.icons = [
                  data.slaunchZone, 
                  data.hPlatform, 
                  data.shortBrick, 
                  data.stone, 
                  data.smallPig, 
                  data.tnt, 
                  data.sblackhole, 
                  data.swormhole, 
                  data.seesaw
                  ]
    data.names = [
                  "Launch Zone", 
                  "Long Brick", 
                  "Short Brick", 
                  "Stone", 
                  "Pig", 
                  "TNT", 
                  "Blackhole", 
                  "Wormhole", 
                  "Seesaw"
                  ]
    data.sizes = [
                  75, 
                  (204, 20), 
                  (84, 20), 
                  18, 
                  15, 
                  (50, 50), 
                  80, 
                  45, 
                  (204, 20)
                  ]
    x, y, distance = 50, 670, 25
    for i in range(len(data.icons)):
        if i > 0:
            width1 = data.icons[i-1].get_width()//2
            width2 = data.icons[i].get_width()//2
            x += width1 + width2 + distance
        newButton = ImageButton(x, y, data.icons[i], data.names[i])
        data.editorIcons += [newButton]

def initSceneButtons(data):
    data.scenebuttons = []
    margin = 100
    x, y = data.width//2, data.topbound + margin
    fontsize, distance = 26, 50
    records = listFiles("scenes")
    for record in records:
        y += distance
        newButton = SceneButton(x, y, record)
        data.scenebuttons += [newButton]    

def chooseEditorButton(data, event):
    if not (data.showInstruction or data.selectScenes):
        for button in data.editorButtons:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False
        for button in data.editorIcons:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False
    else:
        for button in data.editorButtons:
            if (button.text == "back") or \
               (button.text == "instruction" and (not data.selectScenes)) or \
               (button.text == "load" and (not data.showInstruction)):
                if clickOnButton(button, event.pos):
                    button.mouseOnButton = True
                else: button.mouseOnButton = False

def chooseScenesButton(data, event):
    if data.selectScenes:
        for button in data.scenebuttons:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False

def placeItem(data, event):
    if not (data.showInstruction or data.selectScenes):
        if data.dragging:
            if data.autoAlign:
                x, y = automaticAlignment(data, event)
            else:
                x, y = event.pos
            index = data.names.index(data.currItem)
            image = data.reals[index]
            size = data.sizes[index]
            if type(size) == int: # circle
                shape = [x, y, size]
                placeCircle(shape, image, data)
            elif type(size) == tuple: # rect
                if data.rotate: 
                    height, width = size
                    if data.currItem == "Long Brick": 
                        image = data.vPlatform
                    if data.currItem == "Short Brick": 
                        image = data.broder
                else: 
                    width, height = size
                shape = [x-width//2, y-height//2, x+width//2, y+height//2]
                placeRect(shape, image, data)
            data.dragging = False
            data.currItem = None
            data.currPage = -1
            data.rotate = False
            data.error = None
            data.fileSaved = False

def automaticAlignment(data, event):
    data.autoRadius = 20
    x, y = event.pos
    if data.editHistory != []:
        if data.currItem == "Long Brick" or data.currItem == "Short Brick":
            x, y = bricksAlignment(data, event)
        elif data.currItem == "Pig":
            x, y = pigsAlignment(data, event)
        elif data.currItem == "TNT":
            x, y = tntsAlignment(data, event)
        elif data.currItem == "Stone":
            x, y = stonesAlignment(data, event)
    return x, y 

def bricksAlignment(data, event):
    x, y = event.pos
    try:
        if data.currItem == "Long Brick":
            if data.rotate: hbrick, vbrick = 11, 103
            else: hbrick, vbrick = 103, 11
        elif data.currItem == "Short Brick":
            if data.rotate: hbrick, vbrick = 11, 43
            else: hbrick, vbrick = 43, 11                
        for item in data.editHistory[data.currPage]:
            if item.name == "Long Brick" or \
               item.name == "Short Brick" or \
               item.name == "Seesaw":
                left, top, right, bot = item.rect
                lcx, lcy = left - hbrick, (top + bot)//2
                tcx, tcy = (left + right)//2, top - vbrick
                rcx, rcy = right + hbrick, (top + bot)//2
                bcx, bcy = (left + right)//2, bot + vbrick
                centers = [(lcx, lcy), (tcx, tcy), (rcx, rcy), (bcx, bcy)]
                for (cx, cy) in centers:
                    distance = getDistance(cx, cy, x, y)
                    if distance <= data.autoRadius:
                        x, y = cx, cy
        return x, y 
    except:
        return x, y

def pigsAlignment(data, event):
    x, y = event.pos
    diameter = 31
    nearestPigIndex = findNearestTarget(data, x, y, "Pig")
    if nearestPigIndex == None: return x, y
    try:
        nearestPig = data.editHistory[data.currPage][nearestPigIndex]
        cx, cy, r = nearestPig.circle
        lcx, lcy = cx - diameter, cy
        tcx, tcy = cx, cy - diameter
        rcx, rcy = cx + diameter, cy
        bcx, bcy = cx, cy + diameter
        centers = [(lcx, lcy), (tcx, tcy), (rcx, rcy), (bcx, bcy)]
        for (pcx, pcy) in centers:
            distance = getDistance(pcx, pcy, x, y)
            if distance <= data.autoRadius:
                x, y = pcx, pcy
        return x, y
    except:
        return x, y

def stonesAlignment(data, event):
    x, y = event.pos
    diameter = 37
    nearestStoneIndex = findNearestTarget(data, x, y, "Stone")
    if nearestStoneIndex == None: return x, y
    try:
        nearestStone = data.editHistory[data.currPage][nearestStoneIndex]
        cx, cy, r = nearestStone.circle
        lcx, lcy = cx - diameter, cy
        tcx, tcy = cx, cy - diameter
        rcx, rcy = cx + diameter, cy
        bcx, bcy = cx, cy + diameter
        centers = [(lcx, lcy), (tcx, tcy), (rcx, rcy), (bcx, bcy)]
        for (pcx, pcy) in centers:
            distance = getDistance(pcx, pcy, x, y)
            if distance <= data.autoRadius:
                x, y = pcx, pcy
        return x, y 
    except:
        return x, y   

def tntsAlignment(data, event):
    x, y = event.pos
    diameter = 51
    nearestTNTIndex = findNearestTarget(data, x, y, "TNT")
    if nearestTNTIndex == None: return x, y
    try:
        nearestTNT = data.editHistory[data.currPage][nearestTNTIndex]
        left, top, right, bot = nearestTNT.rect
        cx, cy = (left + right)//2, (top + bot)//2
        lcx, lcy = cx - diameter, cy
        tcx, tcy = cx, cy - diameter
        rcx, rcy = cx + diameter, cy
        bcx, bcy = cx, cy + diameter
        centers = [(lcx, lcy), (tcx, tcy), (rcx, rcy), (bcx, bcy)]
        for (pcx, pcy) in centers:
            distance = getDistance(pcx, pcy, x, y)
            if distance <= data.autoRadius:
                x, y = pcx, pcy
        return x, y 
    except:
        return x, y      

def findNearestTarget(data, x, y, target):
    minDistance = None
    minIndex = None
    for item in data.editHistory[data.currPage]:
        if item.name == target:
            try: 
                cx, cy, r = item.circle
            except: 
                left, top, right, bot = item.rect
                cx, cy = (left + right)//2, (top + bot)//2
            distance = getDistance(cx, cy, x, y)
            if minDistance == None or distance < minDistance:
                minDistance = distance
                minIndex = data.placements.index(item)
    return minIndex

def placeCircle(shape, image, data):
    if isPlaceable(shape, data):
        if not data.createNew:
            replaceItem = CircleItem(*(shape + [image, data.currItem]))
            data.placements[data.itemID] = replaceItem
            data.itemID = None
        else:
            newItem = CircleItem(*(shape + [image, data.currItem]))
            data.placements += [newItem]
            data.createNew = False
        newRecord = data.placements[:]
        data.editHistory += [newRecord]

def placeRect(shape, image, data):
    if isPlaceable(shape, data):
        if not data.createNew:
            replaceItem = RectItem(*(shape + [image, data.currItem]))
            data.placements[data.itemID] = replaceItem 
            data.itemID = None                       
        else:
            newItem = RectItem(*(shape + [image, data.currItem]))
            data.placements += [newItem]
            data.createNew = False
        newRecord = data.placements[:]
        data.editHistory += [newRecord]

def isPlaceable(shape, data):
    circleParas, rectParas = 3, 4
    if len(shape) == circleParas:
        if not circleIsPlaceable(shape, data): 
            return False
        x, y, r = shape
        left, top, right, bot = x-r, y-r, x+r, y+r
    if len(shape) == rectParas:
        if not rectIsPlaceable(shape, data): 
            return False
        left, top, right, bot = shape
    if left < 0 or right > data.width or \
       top < data.topbound or bot > data.botbound:
        return False
    return True

def circleIsPlaceable(circle, data):
    for item in data.placements:
        index = data.placements.index(item)
        if index != data.itemID:
            try: 
                result = circlesOverlap(circle, item.circle)
            except: 
                result = rectCircleOverlap(item.rect, circle)
            if result: 
                return False
    return True

def rectIsPlaceable(rect, data):
    for item in data.placements:
        index = data.placements.index(item)
        if index != data.itemID:
            try: 
                result = rectCircleOverlap(rect, item.circle)
            except: 
                result = rectsOverlap(rect, item.rect)
            if result: 
                return False
    return True

def circlesOverlap(circle1, circle2):
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2
    distance = getDistance(x1, y1, x2, y2)
    return distance <= r1 + r2

def rectsOverlap(rect1, rect2):
    left1, top1, right1, bot1 = rect1
    left2, top2, right2, bot2 = rect2
    for x in range(left1, right1+1):
        for y in range(top1, bot1+1):
            if left2 <= x <= right2 and top2 <= y <= bot2: 
                return True
    return False

def rectCircleOverlap(rect, circle):
    left, top, right, bot = rect  
    cx, cy, radius = circle
    for x in range(left, right+1):
        for y in range(top, bot+1):
            # check each pixel in rect: if it's in the circle
            distance = getDistance(x, y, cx, cy)
            if distance <= radius: return True
    return False 

def editorButtonResponse(data, event):
    if not (data.showInstruction or data.selectScenes):
        for button in data.editorButtons:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)
        for button in data.editorIcons:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)
                data.createNew = True
        for item in data.placements:
            try:
                if CircleItem.clickOnCircleItem(item, event.pos):
                    item.buttonFunction(data)
                    data.itemID = data.placements.index(item)
            except:
                if RectItem.clickOnRectItem(item, event.pos):
                    item.buttonFunction(data)
                    data.itemID = data.placements.index(item)
                    if item.name == "Long Brick" or \
                       item.name == "Short Brick":
                        left, top, right, bot = item.rect
                        if right - left < bot - top: 
                            data.rotate = True
    else:
        for button in data.editorButtons:
            if (button.text == "back") or \
               (button.text == "instruction" and (not data.selectScenes)) or \
               (button.text == "load" and (not data.showInstruction)):
                if clickOnButton(button, event.pos):
                    button.buttonFunction(data)

def sceneButtonResponse(data, event):
    if data.selectScenes:
        for button in data.scenebuttons:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)


####################################
# Xlevel
####################################  
    
def initLevelX(data):

    def initPlacements(data):
        # set up parameters
        data.bricks = []
        data.coeff = 0.2
        data.pigs = 0
        pts = 15
        # place items
        finalPlacements = data.editHistory[data.currPage][:]
        for item in finalPlacements:
            try:
                left, top, right, bot = item.rect
                width, height = right - left, bot - top
                x, y = (left + right)//2, (top + bot)//2
            except:
                x, y, r = item.circle
            y = data.height - y
            if item.name == "Long Brick" or item.name == "Short Brick":
                len1, len2, half = 204, 84, 10
                if width == len1:
                    newBrick = Brick(x, y, len1, half, data.hPlatform, data)
                elif width == len2:
                    newBrick = Brick(x, y, len2, half, data.shortBrick, data)
                if height == len1:
                    newBrick = vBrick(x, y, half, len1, data.vPlatform, data)
                elif height == len2:
                    newBrick = vBrick(x, y, half, len2, data.broder, data)
                data.bricks.append(newBrick)
            elif item.name == "Pig":
                newPig = Pig(x, y, r, data.smallPig, data)
                data.objects.append(newPig)
                data.pigs += 1
            elif item.name == "Stone":
                newStone = Stone(x, y, data.stone, data)
                data.objects.append(newStone)
            elif item.name == "TNT":
                affactRadius = 200
                newBomb = Bomb(x, y, affactRadius, data.tnt)
                data.bombs.append(newBomb)  
            elif item.name == "Blackhole":
                affactRadius = 80
                newBlackhole = Blackhole(x, y, affactRadius, data.blackhole)
                data.blackholes.append(newBlackhole)
            elif item.name == "Wormhole":
                newWormhole = Wormhole(x, y, data.wormhole, data)
                data.wormholes.append(newWormhole)    
            elif item.name == "Seesaw":
                height = 10
                newSeesaw = Seesaw(x, y, width, height, data.seesaw, data)
                data.seesaws.append(newSeesaw) 
            elif item.name == "Launch Zone":
                x, y, r = item.circle
                data.launchCx = x
                data.launchCy = y
                data.launchRadius = r 
        # link wormholes
        for i in range(len(data.wormholes)):
            if i % 2 == 0:
                entrance = data.wormholes[i]
                exit = data.wormholes[i+1]
                entrance.link(exit)
        # compute goal
        data.goal = data.pigs * pts
    # init all
    initGameStatus(data)
    initSpace(data)
    initLevelsUI(data)    
    initPaths(data)
    initObjects(data)
    initPlacements(data)


####################################
# Menu
####################################

def initMenu(data):
    data.menuButtons = []
    data.buttonTexts = [
                        "normal game", 
                        "scene editor"
                        ]
    x, y, distance = data.width//2, 420, 70
    for i in range(len(data.buttonTexts)):
        y += distance
        newButton = MenuButton(x, y, data.buttonTexts[i])
        data.menuButtons += [newButton]
    x, y = 60, 650
    newButton = MenuButton(x, y, "quit")
    data.menuButtons += [newButton]

def menuKeyPressed(data, events):
    # do nothing
    pass

def menuMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            chooseMenuButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            menuButtonResponse(data, event)

def menuTimerFired(data):
    # do nothing
    pass

def menuRedrawAll(data, screen):
    screen.blit(data.background, (0, 0))
    x, y = data.width//2, 220
    x -= data.logo.get_width()//2
    y -= data.logo.get_height()//2
    screen.blit(data.logo, (x, y))
    for button in data.menuButtons:
        button.draw(screen, data)

def chooseMenuButton(data, event):
    for button in data.menuButtons:
        if clickOnButton(button, event.pos):
            button.mouseOnButton = True
        else: button.mouseOnButton = False

def menuButtonResponse(data, event):
    for button in data.menuButtons:
        if clickOnButton(button, event.pos):
            button.buttonFunction(data)


####################################
# Submenu
####################################

def initSubmenu(data):
    data.levelButtons = []
    data.submenuButtons = []
    width, height = 256, 175
    distance, radius = 50, 30
    # level buttons
    col, levels = 3, 6
    x0 = data.width//2 - width//2 - distance - width
    y0 = data.height//2 - height//2 - height 
    for level in range(levels):
        x = x0 + (level % col) * (width + distance)
        y = y0 + (level // col) * (height + distance)
        image = eval("data.l" + str(level+1))
        newButton = LevelButton(x, y, width, height, image, level+1)
        data.levelButtons += [newButton]
    # back button
    x, y, distance = data.width//2, 600, 200
    data.submenuButtons = []
    newButton = MenuButton(x, y, "high score")
    data.submenuButtons += [newButton]
    newButton = MenuButton(x - distance, y, "watch replays")
    data.submenuButtons += [newButton]
    newButton = MenuButton(x + distance, y, "instruction")
    data.submenuButtons += [newButton]
    x, y = 60, 650
    newButton = MenuButton(x, y, "back")
    data.submenuButtons += [newButton]

def submenuKeyPressed(data, events):
    # do nothing
    pass

def submenuMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            chooseSubmenuButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            submenuButtonResponse(data, event)

def submenuTimerFired(data):
    # do nothing
    pass

def submenuRedrawAll(data, screen):
    screen.blit(data.background, (0, 0))
    font = pygame.font.Font("Angrybirds-regular.ttf", 36)
    text = font.render("levels", 1 , (0, 0, 0))
    x = data.width//2 - text.get_width()//2
    y = text.get_height()//2
    screen.blit(text, (x, y))
    for button in data.levelButtons:
        button.draw(screen, data)
    for button in data.submenuButtons:
        button.draw(screen, data)

def chooseSubmenuButton(data, event):
    for button in data.levelButtons:
        if clickOnButton(button, event.pos):
            button.mouseOnButton = True
        else: button.mouseOnButton = False
    for button in data.submenuButtons:
        if clickOnButton(button, event.pos):
            button.mouseOnButton = True
        else: button.mouseOnButton = False

def submenuButtonResponse(data, event):
    for button in data.levelButtons:
        if clickOnButton(button, event.pos):
            button.buttonFunction(data)
    for button in data.submenuButtons:
        if clickOnButton(button, event.pos):
            button.buttonFunction(data)


####################################
# Replay menu 
####################################

def initReplayMenu(data):
    data.replayMenuButtons = []
    x, y = 60, 650
    newButton = TextButton(x, y, "back")
    data.replayMenuButtons += [newButton]
    margin = 80
    x, y = data.width//2, margin
    fontsize, distance = 26, 50
    records = listFiles("videos")
    for record in records:
        y += distance
        newButton = VideoButton(x, y, record)
        data.replayMenuButtons += [newButton]    

def replayMenuMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            chooseReplayMenuButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            replayMenuButtonReponse(data, event)

def replayMenuKeyPressed(data, events):
    # do nothing
    pass

def replayMenuTimerFired(data):
    # do nothing
    pass

def replayMenuRedrawAll(data, screen):
    # draw background:
    screen.blit(data.background, (0, 0))
    # draw title:
    fontsize, fontcolor, margin = 36, (0, 0, 0), 50
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    text = font.render("replayer", 1, fontcolor)
    x, y = data.width//2, margin
    x -= text.get_width()//2
    y -= text.get_height()//2
    screen.blit(text, (x, y))
    for button in data.replayMenuButtons:
        button.draw(screen, data)

def chooseReplayMenuButton(data, event):
    for button in data.replayMenuButtons:
        if clickOnButton(button, event.pos):
            button.mouseOnButton = True
        else: button.mouseOnButton = False

def replayMenuButtonReponse(data, event):
    for button in data.replayMenuButtons:
        if clickOnButton(button, event.pos):
            button.buttonFunction(data)


####################################
# Instruction
####################################

def initInstruct(data):
    data.page = 1
    distance = 100
    x, y = data.width//2 + distance, 650
    newButton = TextButton(x, y, "next page")
    data.instructButtons = [newButton]
    x, y = 60, 650
    newButton = TextButton(x, y, "back")
    data.instructButtons += [newButton]
    x, y = data.width//2 - distance, 650
    newButton = TextButton(x, y, "prev page")
    data.instructButtons += [newButton]
    data.characters = [data.redBird2bc, data.yellowBird2bc, data.blueBird2bc,
                       data.greenBird2bc, data.whiteBird2bc, None, 
                       data.swormhole, data.sblackhole, data.tnt]

def instructMousePressed(data, events):
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            chooseInstructButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            instructButtonReponse(data, event)

def instructKeyPressed(data, events):
    # do nothing
    pass

def instructTimerFired(data):
    # do nothing
    pass

def instructRedrawAll(data, screen):
    # draw background:
    screen.blit(data.background, (0, 0))
    # draw title:
    fontsize, fontcolor, margin = 36, (0, 0, 0), 50
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    text = font.render("instruction", 1, fontcolor)
    x, y = data.width//2, margin
    x -= text.get_width()//2
    y -= text.get_height()//2
    screen.blit(text, (x, y))
    for button in data.instructButtons:
        button.draw(screen, data)        
    drawInstruction(screen, data)

def chooseInstructButton(data, event):
    if data.page == 1:
        for button in data.instructButtons[:-1]:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False
    elif data.page == 2:
        for button in data.instructButtons[1:]:
            if clickOnButton(button, event.pos):
                button.mouseOnButton = True
            else: button.mouseOnButton = False        

def instructButtonReponse(data, event):
    if data.page == 1:
        for button in data.instructButtons[:-1]:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)
    elif data.page == 2:
        for button in data.instructButtons[1:]:
            if clickOnButton(button, event.pos):
                button.buttonFunction(data)

def drawInstruction(screen, data):
    fontsize, fontcolor, margin, distance = 24, (0, 0, 0), 150, 50
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize) 
    if data.page == 1:
        texts = [
                 "WELCOME TO ANGRY BIRDS!!!",
                 "rules to win: shoot birds and clear all piggies, have fun!",
                 "some things to notice:",
                 "\t\t\t\t1. this is a world where there is no friction;",
                 "\t\t\t\t2. you have infinite birds but each costs you some "+
                            "scores, scores can be negative;",
                 "\t\t\t\t3. each piglet cleared award you 15 pts;",
                 "\t\t\t\t4. if your birds fly fast enough, they may fly "+
                            "through walls, so do piggies;",
                 "\t\t\t\t5. you can watch replays of your previous games;",
                 "\t\t\t\t6. some birds have special abilities, see next "+
                            "page for details."
                 ]
    elif data.page == 2:
        texts = [
                 "no special abilities, just try to hit piggies (cost: 2);",
                 "special ability: accelerate by 50%  of current speed "+
                                   "(cost: 3);",
                 "special ability: create two dopplegangers to hit pigs "+
                                   "(cost: 5);",
                 "special ability: apply an impulse targeting at where it "+
                                   "was launched (cost: 8);",
                 "special ability: explode and apply impulses to all piggies "+
                                   "close enough (cost: 15);",
                 "\n",
                 "wormhole: transfer a bird (bird only) to another wormhole;",
                 "balckhole: absorb everything when they enter its affecting "+
                             "radius;",
                 "tnt: explode!!!"
                 ]
        x, y, distance, empty = 80, 70, 51, 65
        for i in range(len(data.characters)):
            if data.characters[i] == None: y += empty
            else:
                y += distance
                screen.blit(data.characters[i], (x, y))
    x, y, distance = 150, 70, 25
    for i in range(len(texts)):
        text = font.render(texts[i], 1, fontcolor)
        y += text.get_height() + distance
        screen.blit(text, (x, y))


####################################
# High scores
####################################

def initHighscores(data):
    data.scoreButtons = []
    x, y = 60, 650
    newButton = TextButton(x, y, "back")
    data.scoreButtons += [newButton]
    x, y = 960, 650
    newButton = TextButton(x, y, "clear")
    data.scoreButtons += [newButton]

def highscoreMousePressed(data, events): 
    for event in events:
        if event.type == MOUSEMOTION and event.buttons == (0, 0, 0):
            chooseScoreButton(data, event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            scoreButtonResponse(data, event)

def chooseScoreButton(data, event):
    for button in data.scoreButtons:
        if clickOnButton(button, event.pos):
            button.mouseOnButton = True
        else: button.mouseOnButton = False

def scoreButtonResponse(data, event):
    for button in data.scoreButtons:
        if clickOnButton(button, event.pos):
            button.buttonFunction(data)

def highscoreKeyPressed(data, events):
    # do nothing
    pass

def highscoreTimerFired(data):
    # do nothing
    pass

def highscoreRedrawAll(data, screen):
    # background
    screen.blit(data.background, (0, 0))
    # draw title
    fontsize, fontcolor, margin = 36, (0, 0, 0), 50
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    text = font.render("high scores", 1, fontcolor)
    x, y = data.width//2, margin
    x -= text.get_width()//2
    y -= text.get_height()//2
    screen.blit(text, (x, y))
    # draw button
    for button in data.scoreButtons:
        button.draw(screen, data)
    # draw records:
    try:
        scoreRecords = readFile("score.txt")
        scoreRecords = eval(scoreRecords)
        if scoreRecords == {}: drawNoRecrds(screen, data)
        data.sortedResult = sortDict(scoreRecords)
        fontsize = 26
        font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
        x, y, distance = 422, 150, 50
        for record in data.sortedResult:
            level, score = record[0], record[1]
            text = font.render(level.upper() + ": " + score, 1, fontcolor)
            y += distance
            screen.blit(text, (x, y))
    except:
        drawNoRecrds(screen, data)

def drawNoRecrds(screen, data):
    fontsize, fontcolor = 26, (0, 0, 0)
    font = pygame.font.Font("Angrybirds-regular.ttf", fontsize)
    x, y = data.width//2, data.height//2
    text = font.render("no records so far", 1, fontcolor)
    x -= text.get_width()//2
    y -= text.get_height()//2
    screen.blit(text, (x, y))


####################################
# Button class
####################################

class LevelButton(RectButton):

    def __init__(self, left, top, width, height, image, level):
        super().__init__(left, top, width, height, image)
        self.level = level
        self.chosenColor = (0, 128, 255)

    def buttonFunction(self, data):
        mode = "level" + str(self.level)
        data.mode = mode
        funcName = "initLevel" + str(self.level) + "(data)"
        eval(funcName)
        return

    def draw(self, screen, data):
        if self.mouseOnButton:
            pygame.draw.rect(screen, self.chosenColor, self.background)
        else:
            pygame.draw.rect(screen, self.normalColor, self.background)
        screen.blit(self.image, (self.left, self.top))

class MenuButton(RectButton):

    def __init__(self, cx, cy, text):
        self.fontsize = 30
        self.font = pygame.font.Font("Angrybirds-regular.ttf", self.fontsize)
        self.cx = cx
        self.cy = cy
        self.text = text
        self.mouseOnButton = False
        self.chosenColor = (0, 128, 255)
        self.normalColor = (0, 0, 0)
        self.normalText = self.font.render(self.text,1,self.normalColor)
        self.chosenText = self.font.render(self.text.upper(),1,self.chosenColor)
        self.left = self.cx - self.normalText.get_width()//2
        self.right = self.cx + self.normalText.get_width()//2
        self.top = self.cy - self.normalText.get_height()//2
        self.bot = self.cy + self.normalText.get_height()//2
        self.bounds = [self.left, self.top, self.right, self.bot]

    def draw(self, screen, data):
        if self.mouseOnButton:
            screen.blit(self.chosenText, (self.left, self.top))
        else:
            screen.blit(self.normalText, (self.left, self.top))

    def buttonFunction(self, data):
        if data.mode == "menu":
            if self.text == "normal game":
                data.mode = "submenu"
                initSubmenu(data)
            elif self.text == "scene editor":
                data.mode = "editor"
                initEditor(data)
            elif self.text == "quit":
                pygame.quit()
        elif data.mode == "submenu":
            if self.text == "back":
                data.mode = "menu"
                initMenu(data)
            elif self.text == "watch replays":
                data.mode = "replayMenu"
                initReplayMenu(data)
            elif self.text == "instruction":
                data.mode = "instruct"
                initInstruct(data)
            elif self.text == "high score":
                data.mode = "score"
                initHighscores(data)

class TextButton(RectButton):

    def __init__(self, cx, cy, text):
        self.fontsize = 26
        self.font = pygame.font.Font("Angrybirds-regular.ttf", self.fontsize)
        self.cx = cx
        self.cy = cy
        self.text = text
        self.mouseOnButton = False
        self.chosenColor = (255, 255, 0)
        self.normalColor = (255, 255, 255)
        self.normalText = self.font.render(self.text, 1, self.normalColor)
        self.chosenText = self.font.render(self.text.upper(),1,self.chosenColor)
        self.left = self.cx - self.normalText.get_width()//2
        self.right = self.cx + self.normalText.get_width()//2
        self.top = self.cy - self.normalText.get_height()//2
        self.bot = self.cy + self.normalText.get_height()//2
        self.bounds = [self.left, self.top, self.right, self.bot]

    def draw(self, screen, data):
        if self.mouseOnButton:
            screen.blit(self.chosenText, (self.left, self.top))
        else:
            screen.blit(self.normalText, (self.left, self.top))

    def buttonFunction(self, data):
        if data.mode == "replay":
            if self.text == "back":
                if data.prevMode == "level":
                    data.mode = "submenu"
                    initSubmenu(data)
                elif data.prevMode == "submenu":
                    data.mode = "replayMenu"
                    initReplayMenu(data)
            elif self.text == "replay":
                data.mode == "replay"
                initReplay(data)
        elif data.mode == "replayMenu" or \
             data.mode == "instruct" or \
             data.mode == "score":
            if self.text == "back":
                data.mode = "submenu"
                initSubmenu(data)
        if data.mode == "instruct":
            if self.text == "next page":
                data.page += 1
                data.instructButtons[0].mouseOnButton = False
            elif self.text == "prev page":
                data.page -= 1
                data.instructButtons[-1].mouseOnButton = False
        if data.mode == "score":
            if self.text == "clear":
                scoreRecords = dict()
                writeFile("score.txt", str(scoreRecords))

class SceneButton(TextButton):

    def __init__(self, cx, cy, text):
        super().__init__(cx, cy, text)

    def buttonFunction(self, data):
        initEditor(data)
        circleParas, rectParas = 3, 4
        items = readFile("scenes/" + self.text)
        items = items.splitlines()
        for item in items:
            shape, name = item.split("\t")
            shape = eval(shape)
            index = data.names.index(name)
            image = data.reals[index] 
            if len(shape) == circleParas:
                newItem = CircleItem(*(shape + [image, name]))
                data.placements.append(newItem)
            if len(shape) == rectParas:
                newItem = RectItem(*(shape + [image, name]))
                data.placements.append(newItem)
        newRecord = data.placements[:]
        data.editHistory += [newRecord]

class VideoButton(SceneButton):

    def __init__(self, x, y, text):
        super().__init__(x, y, text)
        self.chosenColor = (0, 128, 255)
        self.normalColor = (0, 0, 0)
        self.normalText = self.font.render(self.text, 1, self.normalColor)
        self.chosenText = self.font.render(self.text.upper(),1,self.chosenColor)

    def buttonFunction(self, data):
        records = readFile("videos/" + self.text)
        data.record = eval(records)
        data.mode = "replay"
        initReplay(data)
        data.prevMode = "submenu"

class ImageButton(RectButton):

    def __init__(self, x, y, image, name):
        self.x = x
        self.y = y
        self.image = image
        self.name = name
        self.fontsize = 18
        self.font = pygame.font.Font("Angrybirds-regular.ttf", self.fontsize)
        self.color = (255, 255, 255)
        self.text = self.font.render(self.name, 1, self.color)
        self.left = self.x - self.image.get_width()//2
        self.right = self.x + self.image.get_width()//2
        self.top = self.y - self.image.get_height()//2
        self.bot = self.y + self.image.get_height()//2
        self.bounds = [self.left, self.top, self.right, self.bot]
        self.bartop = 640
        self.textAnchor = (self.x - self.text.get_width()//2,
                           self.bartop - self.text.get_height())
        self.mouseOnButton = False
        self.up = 5

    def draw(self, screen, data):
        if self.mouseOnButton:
            screen.blit(self.image, (self.left, self.top - self.up))
            screen.blit(self.text, self.textAnchor)
        else:
            screen.blit(self.image, (self.left, self.top))

    def buttonFunction(self, data):
        data.dragging = True
        data.currItem = self.name

class RectItem(RectButton):

    def __init__(self, left, top, right, bot, image, name):
        self.left = left
        self.top = top
        self.right = right
        self.bot = bot
        self.rect = [self.left, self.top, self.right, self.bot]
        self.mouseOnButton = False
        self.x = (self.left + self.right)//2
        self.y = (self.top + self.bot)//2
        self.image = image
        self.blitx = self.x - self.image.get_width()//2
        self.blity = self.y - self.image.get_height()//2
        self.name = name

    def draw(self, screen, data):
        screen.blit(self.image, (self.blitx, self.blity))

    def buttonFunction(self, data):
        data.dragging = True
        data.currItem = self.name

    @staticmethod
    def clickOnRectItem(rectItem, click):
        left, top, right, bot = rectItem.rect
        x, y = click
        return left <= x <= right and top <= y <= bot

class CircleItem(CircleButton):

    def __init__(self, cx, cy, radius, image, name):
        super().__init__(cx, cy, radius, image)
        self.circle = [self.cx, self.cy, self.radius]
        self.name = name

    def draw(self, screen, data):
        screen.blit(self.image, (self.left, self.top))

    def buttonFunction(self, data):
        data.dragging = True
        data.currItem = self.name

    @staticmethod
    def clickOnCircleItem(circleItem, click):
        cx, cy, radius = circleItem.circle
        x, y = click
        distance = getDistance(cx, cy, x, y)
        return distance <= radius

class ToolBarButton(TextButton):

    def buttonFunction(self, data):
        if not (data.showInstruction or data.selectScenes):
            if self.text == "back":
                data.mode = "menu"
                initMenu(data)
            elif self.text == "clear":
                initEditor(data)
            elif self.text == "save":
                ToolBarButton.save(data)
            elif self.text == "undo":
                ToolBarButton.undo(data)
            elif self.text == "redo":
                ToolBarButton.redo(data)
            elif self.text == "play":
                checkResult = ToolBarButton.checkItem(data)
                if checkResult == None:
                    data.mode = "levelX"
                    initLevelX(data)
                else:
                    data.error = checkResult
        else:
            if self.text == "back":
                if data.showInstruction:
                    data.showInstruction = not data.showInstruction
                if data.selectScenes:
                    data.selectScenes = not data.selectScenes

    @staticmethod
    def save(data):
        if data.editHistory != []:
            finalPlacements = data.editHistory[-1][:]
            for item in finalPlacements:
                try: shape = item.rect
                except: shape = item.circle
                data.contents += str(shape) + "\t" + item.name + "\n"
            currTime = getCurrentTime()
            filename = "scenes/NEW SCENE MADE AT " + currTime + ".TXT"
            writeFile(filename, data.contents)
        data.contents = ""
        data.fileSaved = True

    @staticmethod
    def undo(data):
        data.fileSaved = False
        if abs(data.currPage) <= len(data.editHistory)+1:
            data.currPage -= 1
            data.undoCount += 1
            if abs(data.currPage) <= len(data.editHistory):
                newRecord = data.editHistory[data.currPage][:]
                data.editHistory += [newRecord]
                data.currPage -= 1

    @staticmethod
    def redo(data):
        data.fileSaved = False
        if data.redoCount < data.undoCount:
            if data.currPage < -1:
                data.currPage += 1
                data.redoCount += 1
                if abs(data.currPage) <= len(data.editHistory):
                    newRecord = data.editHistory[data.currPage][:]
                    data.editHistory += [newRecord]
                    data.currPage -= 1

    @staticmethod
    def checkItem(data):
        text = None
        font = pygame.font.Font("Angrybirds-regular.ttf", 26)
        if data.editHistory != []:
            finalPlacements = data.editHistory[data.currPage][:]
            for item in finalPlacements:
                if item.name == "Launch Zone":
                    data.launchZonesCount += 1
                elif item.name == "Pig":
                    data.pigCount += 1
                elif item.name == "Wormhole":
                    data.wormholeCount += 1
            if data.launchZonesCount > 1:
                text = "game cannot start: more than 1 launch zones!"
            elif data.launchZonesCount < 1:
                text = "game cannot start: no launch zones!"
            elif data.pigCount < 1:
                text = "game cannot start: no pigs!"
            elif data.wormholeCount % 2 == 1:
                text = "game cannot start: odd numbers of wormholes!"
        else: 
            text = "game cannot start: no contents placed!"
        if text != None: 
            text = font.render(text, 1, (0, 0, 0))
        data.launchZonesCount = 0
        data.pigCount = 0
        data.wormholeCount = 0
        return text

class StatusButton(TextButton):

    def __init__(self, cx, cy, text):
        super().__init__(cx, cy, text)
        self.switchOnColor = (0, 255, 0)
        self.switchOnText = self.font.render(self.text, 1, self.switchOnColor)

    def draw(self, screen, data):
        if data.autoAlign and self.text == "auto-align":
            if not self.mouseOnButton:
                screen.blit(self.switchOnText, (self.left, self.top))
        if data.showInstruction and self.text == "instruction":
            if not self.mouseOnButton:
                screen.blit(self.switchOnText, (self.left, self.top))
        if data.selectScenes and self.text == "load":
            if not self.mouseOnButton:
                screen.blit(self.switchOnText, (self.left, self.top))
        if self.mouseOnButton:
            screen.blit(self.chosenText, (self.left, self.top))
        else:
            if not data.autoAlign and self.text == "auto-align":
                screen.blit(self.normalText, (self.left, self.top))
            elif not data.showInstruction and self.text == "instruction":
                screen.blit(self.normalText, (self.left, self.top))
            elif not data.selectScenes and self.text == "load":
                screen.blit(self.normalText, (self.left, self.top))

    def buttonFunction(self, data):
        if self.text == "auto-align":
            data.autoAlign = not data.autoAlign
        if self.text == "instruction":
            data.showInstruction = not data.showInstruction
        if self.text == "load":
            data.selectScenes = not data.selectScenes
            if data.selectScenes:
                initSceneButtons(data)
