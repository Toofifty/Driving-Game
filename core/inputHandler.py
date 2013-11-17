# inputHandler
import pygame
from pygame.locals import *

def handleKeys(car):
    """  
        Handles key events and key strokes for the main class
    """
    for event in pygame.event.get():
        if hasattr(event, 'key'):
            down = event.type == KEYDOWN
            if event.key == K_RIGHT: car.k_right = down * -car.TURN_SPEED
            elif event.key == K_LEFT: car.k_left = down * car.TURN_SPEED
            elif event.key == K_UP: 
                car.k_up = down * 50
            elif event.key == K_DOWN: car.k_down = -1 * down * 50
            elif event.key == K_SPACE and event.type == 2: car.handbrake = True   
            elif event.key == K_SPACE and event.type == 3: car.handbrake = False            
            elif event.key == K_ESCAPE and event.type == 2: 
                return 'pause'
            elif event.key == K_RETURN and event.type == 2: 
                return 'reset'
            elif event.key == K_c and event.type == 2: 
                return 'newColour'

def handleMenuKeys(stuff):
    print 'handleMenuKeys'
    #do stuff