import pygame


def loadImages(data):
    # logo
    # image from: 
    # http://freeangrybirdsgame.org/
    data.logo = pygame.image.load("images/logo.png")
    # game scene
    # images from: 
    # http://www.iconarchive.com/tag/angry-birds;
    # http://puffleville.wikia.com/wiki/File:INGAME_BLOCKS_MISC_1.png
    # http://angrybirds.wikia.com/wiki/File:INGAME_BLOCKS_STONE_1.png
    data.largePig = pygame.image.load("images/largePig.png")
    data.smallPig = pygame.image.load("images/pig.png")
    data.launchZone = pygame.image.load("images/launchZone.png")
    data.hPlatform = pygame.image.load("images/hPlatform.png")
    data.vPlatform = pygame.image.load("images/vPlatform.png")
    data.platform = pygame.image.load("images/shortPlatform.png")
    data.blackhole = pygame.image.load("images/blackhole.png")
    data.tnt = pygame.image.load("images/tnt.png")
    data.wormhole = pygame.image.load("images/wormhole.png")
    data.shortPlatform = pygame.image.load("images/broder.png")
    data.seesaw = pygame.image.load("images/seesaw.png")
    data.wormhole = pygame.image.load("images/wormhole.png")
    data.stone = pygame.image.load("images/stone.png")  
    # level cleared  
    # images from: 
    # peggle.wikia.com
    data.star1 = pygame.image.load("images/star1.png")
    data.star2 = pygame.image.load("images/star2.png")
    data.star3 = pygame.image.load("images/star3.png")
    # explosion images
    # images from: 
    # http://www.iconarchive.com/tag/angry-birds
    data.phase0 = pygame.image.load("images/phase0.png")
    data.phase1 = pygame.image.load("images/phase1.png")
    data.phase2 = pygame.image.load("images/phase2.png")
    data.phase3 = pygame.image.load("images/phase3.png")
    # birds in game
    # images from: 
    # http://www.iconarchive.com/tag/angry-birds
    data.redBird = pygame.image.load("images/red.png")
    data.blueBird = pygame.image.load("images/blue.png")
    data.yellowBird = pygame.image.load("images/yellow.png")
    data.whiteBird = pygame.image.load("images/white.png")
    data.greenBird = pygame.image.load("images/green.png")
    # original
    # images from: 
    # http://www.iconarchive.com/tag/angry-birds
    data.current = pygame.image.load("images/current.png")
    data.redBird2bc = pygame.image.load("images/red2bc.png")
    data.blueBird2bc = pygame.image.load("images/blue2bc.png")
    data.yellowBird2bc = pygame.image.load("images/yellow2bc.png")
    data.whiteBird2bc = pygame.image.load("images/white2bc.png")
    data.greenBird2bc = pygame.image.load("images/green2bc.png")
    # when selected
    # images from:
    # http://www.iconarchive.com/tag/angry-birds
    data.redChosen = pygame.image.load("images/redChosen.png")
    data.blueChosen = pygame.image.load("images/blueChosen.png")
    data.yellowChosen = pygame.image.load("images/yellowChosen.png")
    data.whiteChosen = pygame.image.load("images/whiteChosen.png")
    data.greenChosen = pygame.image.load("images/greenChosen.png")
    # editor
    # images from: 
    # http://angrybirds.wikia.com/wiki/File:INGAME_BLOCKS_STONE_1.png
    data.sblackhole = pygame.image.load("images/sblackhole.png")
    data.swormhole = pygame.image.load("images/swormhole.png")
    data.broder = pygame.image.load("images/broder.png")
    data.shortBrick = pygame.image.load("images/shortPlatform.png")
    data.slaunchZone = pygame.image.load("images/slaunchZone.png")
    # levels
    data.l1 = pygame.image.load("images/level1.png")
    data.l2 = pygame.image.load("images/level2.png")
    data.l3 = pygame.image.load("images/level3.png")
    data.l4 = pygame.image.load("images/level4.png")
    data.l5 = pygame.image.load("images/level5.png")
    data.l6 = pygame.image.load("images/level6.png")




