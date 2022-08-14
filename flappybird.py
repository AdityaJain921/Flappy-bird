import random # for generating random numbers
import sys
from typing import Mapping # we will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame imports
import os

# GLOBAL VARIABLES FOR THE GAME
FPS = 32
SCREENWIDTH = 593
SCREENHEIGHT = 480

SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'sprites/bird.png'
BACKGROUND = 'sprites/background.png'
PIPE = 'sprites/pipe.png'

def welcomeScreen():
    """
    shows welcome images on the screen
    """
    playerX = int(SCREENWIDTH/5)
    playerY = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messageX = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messageY = int(SCREENHEIGHT * 0.012)
    basex = 0

    while True:
        for event in pygame.event.get():
            # if user clicks on cross buttton, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # if the user presses space or key , start the game for them.
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

            else:
                SCREEN.blit(GAME_SPRITES['background'],(0, 0))
                SCREEN.blit(GAME_SPRITES['player'],(playerX, playerY))
                SCREEN.blit(GAME_SPRITES['message'],(messageX, messageY))
                SCREEN.blit(GAME_SPRITES['base'],(basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    basex = 0
    Score = 0
    playerX = int(SCREENWIDTH/5)
    playerY = int(SCREENWIDTH/2)

    # creates 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    #my list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 10, 'y' : newPipe1[0]['y']},
        {'x': SCREENWIDTH + 10 + (SCREENWIDTH/2), 'y': newPipe2[0]['y']}
    ]

    #my list of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 10, 'y' : newPipe1[1]['y']},
        {'x': SCREENWIDTH + 10 + (SCREENWIDTH/2), 'y': newPipe2[1]['y']}         
    ]

    pipeVelX = -4
    playerVelY = -9  
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapV = -8 #velocity while flapping
    playerFlapped  = False #it is true only when the bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playerY > 0:
                    playerVelY = playerFlapV
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerX, playerY, upperPipes, lowerPipes)
        if crashTest: 
            return
        
        # check for scores
        playerMidPos = playerX + GAME_SPRITES['player'].get_width()/2       
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2 
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                Score += 1
                print(f"Your score is {Score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
            
        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playerY = playerY + min(playerVelY , GROUNDY - playerY - playerHeight)

        # moves pipe to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX
        # add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])
        
        #if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        #lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][0], (lowerPipe['x'], lowerPipe['y']))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerX, playerY))

        myDigits = [int(x) for x in list(str(Score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (xoffset, SCREENHEIGHT * 0.12))
            xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)  

def isCollide(playerX, playerY, upperPipes, lowerPipes):
    if playerY > GROUNDY - 15 or playerY < 0:
        GAME_SOUNDS['hit'].play()
        return True
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playerY <= pipeHeight + pipe['y'] and abs(playerX - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
    for pipe in lowerPipes:
        if(playerY + GAME_SPRITES['player'].get_height()>pipe['y'] and abs(playerX - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True
    return False
    
        
    
def getRandomPipe():
    """
    generate positions of two pipes (one bottom straight and one top rotated) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()) - 1 * offset)
    pipex = SCREENWIDTH + 5
    y1 = pipeHeight - y2 + min(0.8*offset, offset)
    pipe = [ 
        {'x': pipex, 'y': -y1}, # upper pipe
        {'x': pipex, 'y': y2}   # lower pipe   
         ]
    return pipe

if __name__ == "__main__":
    # this will be the main point from where our will start
    pygame.init() # initialise all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('FLAPPY BIRD BY ADITYA')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('sprites/0.png').convert_alpha(),
        pygame.image.load('sprites/1.png').convert_alpha(),
        pygame.image.load('sprites/2.png').convert_alpha(),
        pygame.image.load('sprites/3.png').convert_alpha(),
        pygame.image.load('sprites/4.png').convert_alpha(),
        pygame.image.load('sprites/5.png').convert_alpha(),
        pygame.image.load('sprites/6.png').convert_alpha(),
        pygame.image.load('sprites/7.png').convert_alpha(),
        pygame.image.load('sprites/8.png').convert_alpha(),
        pygame.image.load('sprites/9.png').convert_alpha()
    )
    GAME_SPRITES['message'] = pygame.image.load('sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180), pygame.image.load(PIPE).convert_alpha())

    #GAME SOUNDS
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('audio/wing.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('audio/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('audio/point.mp3')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    print(GAME_SPRITES['background'].get_width())
    while True:
        welcomeScreen()
        mainGame()
    





