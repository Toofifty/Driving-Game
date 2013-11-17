# physicsHandler
import pygame, math
from pygame.locals import *

"""
    Handles physics within the demo.
    RETURNS: True
"""

def carPhysics(car):
    # Store a starting value to check if
    # something's actually happening
    f_ENGINE_o = car.f_ENGINE
    
    # Add or remove from ENGINE force
    car.f_ENGINE += (car.k_up + car.k_down)
    
    # Check old vs. new force
    if car.f_ENGINE == f_ENGINE_o:
        # If no increase to force, stop force
        car.f_ENGINE = 0
    if car.f_ENGINE > car.MAX_FORCE:
        # Cap the FORCE at MAX_FORCE
        car.f_ENGINE = car.MAX_FORCE
    elif car.f_ENGINE < car.MAX_NEGATIVE_FORCE:
        # Cap the reverse FORCE at MAX_NEGATIVE_FORCE
        car.f_ENGINE = car.MAX_NEGATIVE_FORCE
    # Calculate all retarding forces of the car,
    # using values stored in the carSprite object
    f_TRACTION = car.f_ENGINE
    f_DRAG = -1 * car.c_DRAG * car.VELOCITY * math.fabs(car.VELOCITY)
    f_ROLL = -1 * car.c_ROLL * car.VELOCITY
    
    if car.handbrake:
        f_ROLL *= 20
    f_LONG = f_TRACTION + f_DRAG + f_ROLL
    
    # Calculate acceleration, F = ma
    car.ACCELERATION = f_LONG / car.MASS
    # Calculate velocity from acceleration, v = v + at
    # No t value, because this happens every tick (t = 1)
    car.VELOCITY += car.ACCELERATION
    
    # If going more than 1m/s, leave turning as-is
    if math.fabs(car.VELOCITY) > 1:
        car.direction += (car.k_right + car.k_left)
    else: 
        # If not, slow down turning by v^2
        car.direction += car.VELOCITY**2 * (car.k_right + car.k_left)
    
    # Ensure all car angles 0 < x < 360
    if car.direction >= 360:
        car.direction = 0
    if car.direction < 0:
        car.direction += 360
        
    # Calculate new position based on direction, velocity
    x, y = car.position
    rad = car.direction * math.pi / 180
    x += car.VELOCITY*math.sin(rad)
    y += car.VELOCITY*math.cos(rad)
    car.position = (x, y)
    
    # Rotate image to match direction
    car.image = pygame.transform.rotate(car.src_image, car.direction)
    
    # Get new rect (hitbox)
    car.rect = car.image.get_rect()
    car.rect.center = car.position
    
    return True