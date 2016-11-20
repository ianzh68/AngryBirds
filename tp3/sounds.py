import pygame

# this file is written with the help from Tianze Mu (ID: tianzem), 
# who was a S15 5-112 student.

# sounds resources:
# http://soundfxcenter.com/sound_effect/search.php?sfx=angry+bird


sounds = dict()

def loadSounds():
    global sounds
    pygame.mixer.init(44100, -16, 2, 2048)
    pygame.mixer.music.load("sounds/bgm.ogg")
    pygame.mixer.music.play(-1, 0)
    soundsList = [
                  "sounds/fly.ogg",
                  "sounds/fall.ogg",
                  "sounds/tnt.ogg",
                  "sounds/complete.ogg",
                  "sounds/sling.ogg",
                  "sounds/wormhole.ogg"
                  ]
    for name in soundsList:
        sounds[name] = pygame.mixer.Sound(name)

def playSounds(name):
    sounds[name].play()
