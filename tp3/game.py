from core import *
from sounds import *
from images import *


class AngryBird(object):
    # this barebone is created based on the tutorial from:
    # http://blog.lukasperaza.com/getting-started-with-pygame/
    def __init__(self):
        self.width = 1024
        self.height = 700
        self.fps = 70
        self.title = "Angry Bird"
        self.mode = "menu"
        self.playing = True
        self.videos = list()
        loadSounds()
        loadImages(self)

    def init(self):
        if self.mode == "menu":
            initMenu(self)
        elif self.mode == "submenu":
            initSubmenu(self)
        elif self.mode == "replay":
            initReplay(self)
        elif self.mode == "replayMenu":
            initReplayMenu(self)
        elif self.mode == "score":
            initHighscore(self)
        elif self.mode == "instruct":
            initInstruct(self)
        elif self.mode == "editor":
            initEditor(self)
        elif self.mode.startswith("level"):
            eval("initLevel" + self.mode[-1] + "(self)")

    def mousePressed(self, events):
        if self.mode == "menu":
            menuMousePressed(self, events)
        elif self.mode == "submenu":
            submenuMousePressed(self, events)
        elif self.mode.startswith("level"):
            levelsMousePressed(self, events)
        elif self.mode == "replay":
            replayMousePressed(self, events)
        elif self.mode == "replayMenu":
            replayMenuMousePressed(self, events)
        elif self.mode == "editor":
            editorMousePressed(self, events)
        elif self.mode == "instruct":
            instructMousePressed(self, events)
        elif self.mode == "score":
            highscoreMousePressed(self, events)

    def keyPressed(self, events):
        if self.mode == "menu":
            menuKeyPressed(self, events)
        elif self.mode == "submenu":
            submenuKeyPressed(self, events)
        elif self.mode.startswith("level"):
            levelsKeyPressed(self, events)
        elif self.mode == "replay":
            replayKeyPressed(self, events)
        elif self.mode == "replayMenu":
            replayMenuKeyPressed(self, events)
        elif self.mode == "editor":
            editorKeyPressed(self, events)
        elif self.mode == "instruct":
            instructKeyPressed(self, events)
        elif self.mode == "score":
            highscoreKeyPressed(self, events)

    def timerFired(self):
        if self.mode == "menu":
            menuTimerFired(self)
        elif self.mode == "submenu":
            submenuTimerFired(self)
        elif self.mode.startswith("level"):
            levelsTimerFired(self)
        elif self.mode == "replay":
            replayTimerFired(self)
        elif self.mode == "replayMenu":
            replayMenuTimerFired(self)
        elif self.mode == "editor":
            editorTimerFired(self)
        elif self.mode == "instruct":
            instructTimerFired(self)
        elif self.mode == "score":
            highscoreTimerFired(self)

    def redrawAll(self, screen):
        if self.mode == "menu":
            menuRedrawAll(self, screen)
        elif self.mode == "submenu":
            submenuRedrawAll(self, screen)
        elif self.mode.startswith("level"):
            levelsRedrawAll(self, screen)
        elif self.mode == "replay":
            replayRedrawAll(self, screen)
        elif self.mode == "replayMenu":
            replayMenuRedrawAll(self, screen)
        elif self.mode == "editor":
            editorRedrawAll(self, screen)
        elif self.mode == "instruct":
            instructRedrawAll(self, screen)
        elif self.mode == "score":
            highscoreRedrawAll(self, screen)

    def quitEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

    def play(self):
        # init pygame
        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # background
        self.background = pygame.image.load("images/BG1.jpg").convert()
        # set the title of the window
        pygame.display.set_caption(self.title)
        self.init()

        while self.playing:
            # event based game
            events = pygame.event.get()
            self.timerFired()
            self.mousePressed(events)
            self.keyPressed(events)
            self.quitEvents(events)
            self.redrawAll(screen)
            # update screen
            pygame.display.flip()
            clock.tick(self.fps)



