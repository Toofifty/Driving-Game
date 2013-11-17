# cargame.py

# INITIALISATION
# Python and Pygame related
import pygame, math, sys, random, os
from pygame.locals import *
import pygame.mixer
pygame.mixer.init()
pygame.font.init()
pygame.display.init()

# Local classes
import core.inputHandler, core.physicsHandler

# Create window
pygame.display.set_caption("Don't hit the cones!")
scene_image = pygame.image.load('sprites/scene.png')
_, _, WINDOW_WIDTH, WINDOW_HEIGHT = pygame.Rect(scene_image.get_rect())
HALF_WIDTH = int(WINDOW_WIDTH/2)
HALF_HEIGHT = int(WINDOW_HEIGHT/2)
scene = pygame.transform.scale(scene_image, (WINDOW_WIDTH *2, WINDOW_HEIGHT * 2))
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 16)

# Initialise clock
clock = pygame.time.Clock()

# Initialise locals
current_car = 0 
cones = []
colours = [
    'orange',
    'yellow',
    'lime',
    'blue',
    'purple',
]

tick_rate = 30 # (framerate)
version = 'a0.1.0'

def screenText(text, position, size, font, colour):
    font = pygame.font.SysFont(font, size)
    stext = font.render(text, 1, colour)
    screen.blit(stext, position)
        
def pauseMenu(reason):
    pause_screen = pygame.image.load('sprites/pause.png').convert_alpha()
    s_image = pygame.image.load('sprites/spyker_side_orange.png').convert_alpha()
    si_rect = pygame.Rect(s_image.get_rect())
    side_image = pygame.transform.scale(s_image, ((2*si_rect[2],2*si_rect[3])))
    
    screen.blit(pause_screen, (0, 0))
    screen.blit(side_image, (750, 650))
    pygame.display.flip()

    done = False
    while not done:
        for event in pygame.event.get():
            if hasattr(event, 'key'):
                if event.key == K_RETURN: done = True
                elif event.key == K_ESCAPE and event.type == 2: 
                    print 'exit'
                    sys.exit(0)
        
def cmdStats(car):
    os.system('cls' if os.name=='nt' else 'clear')
    print 'Driving demo ' + version + ' @ ' + str(tick_rate) + ' FPS'
    print 'F: ' + str(car.f_ENGINE)
    print 'M: ' + str(car.MASS)
    print 'A: ' + str(car.ACCELERATION)
    print 'V: ' + str(car.VELOCITY)
    print 'R: ' + str(car.f_LONG)
    print 'X: ' + str(car.position[0])
    print 'Y: ' + str(car.position[1])

def simpleCamera(camera, target_rect):
    l, t, tw, th = target_rect
    _, _, w, h = camera
    return Rect(-(l+tw/2)+(HALF_WIDTH), -(t+th/2)+(HALF_HEIGHT), w, h)
    
def complexCamera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h
    
    l = min(0, l)
    l = max(-(camera.width-(WINDOW_WIDTH)), l)
    t = max(-(camera.height-(WINDOW_HEIGHT)), l)
    t = min(0, t)
    return Rect(l, t, w, h)
    
class followCamera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)
        
    def apply(self, target):
        return target.rect.move(self.state.topleft)
        
    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
    
class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    
class carSprite(Entity):
    """ 
        BLURB!
    """
    def __init__(self, image, position, turn_speed, mass, max_force, max_negative_force, c_drag, c_roll):
        # __init__ sprite
        Entity.__init__(self)
        
        # Get variables from arguments
        self.s_image = pygame.image.load(image).convert_alpha()
        self.position = position
        self.TURN_SPEED = turn_speed
        self.MASS = mass
        self.MAX_FORCE = max_force
        self.MAX_NEGATIVE_FORCE = -max_negative_force
        self.c_DRAG = c_drag
        self.c_ROLL = c_roll
        
        # Set all other default/calculated variables
        self.VELOCITY = self.direction = self.f_ENGINE = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0
        self.rect = pygame.Rect(self.s_image.get_rect())
        self.rect.center = self.position  
        self.f_DRAG = 1
        self.f_LONG = 0
        self.handbrake = False
        self.src_image = pygame.transform.scale(self.s_image, (self.rect[2]*2, self.rect[3]*2))
        
    def update(self, deltat):
        # To physics handler (returns True)
        core.physicsHandler.carPhysics(self)
        
        # Display stats in the console
        cmdStats(self)
        
        # Display v, x, and y in-game
        screenText(str(math.floor(self.VELOCITY*36)/10) 
            + 'km/h ' 
            + str(math.floor(10*self.position[0])/10) 
            + 'x ' 
            + str(math.floor(10*self.position[1])/10) 
            + 'y', (20, 20), 25, 'Lucida Console', (255, 255, 255)
        )
        
    def change(self, colour):
        s_image = pygame.image.load('sprites/spyker_' 
            + colours[colour] + '.png').convert_alpha()
        self.rect = pygame.Rect(s_image.get_rect())
        self.src_image = pygame.transform.scale(s_image, (self.rect[2]*2, self.rect[3]*2))
        print colours[colour]
        
    
class coneSprite(Entity):
    """
        The sprite of the cones that can be knocked over
        through use of coneSprite.update(True) and reset if False
    """
    # Load both sprites
    n_img = pygame.image.load('sprites/cone_normal.png').convert_alpha()
    normal = pygame.transform.scale(n_img, (64, 64))
    h_img = pygame.image.load('sprites/cone_hit.png').convert_alpha()
    hit = pygame.transform.scale(h_img, (64, 64))
    def __init__(self, pos):
        # __init__ sprite
        Entity.__init__(self)
        cones.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 10, 10)
        self.image = self.normal
        self.over = False
    def update(self, hit):
        if hit and not self.over: 
            sound = pygame.mixer.music.load('sounds/hit.wav')
            pygame.mixer.music.play(0)
            self.image = pygame.transform.rotate(self.hit, car.direction - 135)
            self.over = True
        elif not hit: 
            self.image = self.normal
            self.over = False	
            
class sceneEntity(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.image = scene
        self.rect = pygame.Rect(self.image.get_rect())
        
# Create a car
car = carSprite(
    'sprites/spyker_orange.png', # image_file
    (220, 100), # position
    5, # turn_speed
    1000, # mass
    10000, # max_force
    1000, # max_negative_force
    10, # c_drag
    10 # c_roll
)
        

cones = [
    coneSprite((200, 200)),
    coneSprite((600, 200)),
    coneSprite((600, 400)),
    coneSprite((200, 400))
]

camera = followCamera(simpleCamera, WINDOW_WIDTH*2, WINDOW_HEIGHT*2)

car_group = pygame.sprite.RenderPlain(car)
cones_group = pygame.sprite.RenderPlain(cones)

while 1:
    # Start clock
    deltat = clock.tick(tick_rate)
    
    # Handle inputs
    action = core.inputHandler.handleKeys(car)
    if action == 'reset': 
        # Reset all cones
        for cone in cones: cone.update(False)
        
        # Spawn new car
        car = carSprite(
            'sprites/spyker_' + colours[current_car] + '.png', # image_file
            (220, 100), # position
            5, # turn_speed
            1000, # mass
            10000, # max_force
            1000, # max_negative_force
            10, # c_drag
            10 # c_roll
        )
        car_group = pygame.sprite.RenderPlain(car)
    elif action == 'newColour':
        # Cycle through car
        current_car += 1
        if current_car > 4: current_car = 0
        
        car.change(current_car)
    elif action == 'pause':
        pauseMenu('user')
        
        
    # Draw the scene
    for cone in cones:
        if car.rect.colliderect(cone): cone.update(True)
    
    screen.fill((0, 0, 0))
    
    
    #cones_group.draw(screen)
    #car_group.draw(screen)
        
    screen.blit(sceneEntity().image, camera.apply(sceneEntity()))
    for cone in cones:
        screen.blit(cone.image, camera.apply(cone))
    car_group.update(deltat)
    camera.update(car)
    screen.blit(car.image, camera.apply(car))
    pygame.display.flip()
    
    
    
    
    
    
    
    
    
    
