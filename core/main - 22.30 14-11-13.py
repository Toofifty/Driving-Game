# cargame.py

# INITIALISATION
import pygame, math, sys, random, os
from pygame.locals import *
import pygame.mixer
pygame.mixer.init()
pygame.font.init()
background = pygame.image.load('sprites/background.png')
b_rect = pygame.Rect(background.get_rect())
metre = 32
screen = pygame.display.set_mode((b_rect[2], b_rect[3]))
clock = pygame.time.Clock()
current_car = 0
tick_rate = 30

colours = [
    'orange',
    'yellow',
    'lime',
    'blue',
    'purple',
]

def screenText(text, position, size, font, colour):
    font = pygame.font.SysFont(font, size)
    stext = font.render(text, 1, colour)
    screen.blit(stext, position)
        
def pauseMenu(reason):
    pygame.event.clear()
    pygame.event.get()
    pygame.time.wait(100)
    done = False
    while not done:
        for event in pygame.event.get():
            if hasattr(event, 'key'):
                if event.key == K_RETURN: done = True
                elif event.key == K_ESCAPE: 
                    print 'exit'
                    sys.exit(0)
        
        
        
class carSprite(pygame.sprite.Sprite):
    TURN_SPEED = 5
    MASS = 1000
    MAX_FORCE = 10000
    c_DRAG = 10
    c_ROLL = 10
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image)
        self.position = position
        self.VELOCITY = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = self.f_ENGINE = 0
        self.k_space = 1
        self.rect = pygame.Rect(self.src_image.get_rect())
        self.rect.center = self.position  
        self.FRICTION = 10
        self.f_DRAG = 1
        self.f_LONG = 0
    def update(self, deltat):
        # PHYSICS
        f_ENGINE_o = self.f_ENGINE
        self.f_ENGINE += (self.k_up + self.k_down)
        if self.f_ENGINE == f_ENGINE_o:
            self.f_ENGINE = 0
        if self.f_ENGINE > self.MAX_FORCE:
            self.f_ENGINE = self.MAX_FORCE
        f_TRACTION = self.f_ENGINE
        f_DRAG = -1 * self.c_DRAG * self.VELOCITY * math.fabs(self.VELOCITY)
        f_ROLL = -1 * self.c_ROLL * self.VELOCITY
        f_LONG = f_TRACTION + f_DRAG + f_ROLL
        self.ACCELERATION = f_LONG / self.MASS
        self.VELOCITY += self.ACCELERATION
        print str(self.VELOCITY) + ' = ' + ' 1/' + str(tick_rate) + ' * ' + str(self.ACCELERATION)
        print 'FORCE: ' + str(self.f_ENGINE) + ' MASS: ' + str(self.MASS) + ' ACCELERATION: ' + str(self.ACCELERATION) + ' VELOCITY: ' + str(self.VELOCITY) + ' RESISTANCE: ' + str(self.f_LONG)
        if math.fabs(self.VELOCITY) > 1:
            self.direction += (self.k_right + self.k_left)
        else: 
            self.direction += self.VELOCITY**2 * (self.k_right + self.k_left)
        if self.direction >= 360:
            self.direction = 0
        if self.direction < 0:
            self.direction += 360
        x, y = self.position
        rad = self.direction * math.pi / 180
        x += self.VELOCITY*math.sin(rad)
        y += self.VELOCITY*math.cos(rad)
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        #os.system('cls' if os.name=='nt' else 'clear')
        #print str(self.VELOCITY) + 'm/s ' + str(x) + 'x ' + str(y) + 'y'
        screenText(str(math.floor(self.VELOCITY*36)/10) + 'km/h ' + str(math.floor(10*x)/10) + 'x ' + str(math.floor(10*y)/10) + 'y', (700, 20), 25, 'Arial', (255, 255, 0))
    def change(self, colour):
        self.src_image = pygame.image.load('sprites/car_' + colours[colour] + '.png')
        print colours[colour]
        pygame.time.wait(100)
        
    
class coneSprite(pygame.sprite.Sprite):
    normal = pygame.image.load('sprites/cone_normal.png')
    hit = pygame.image.load('sprites/cone_hit.png')
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
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
            
pygame.display.set_caption("Don't hit the cones!")
cones = []		
    
# CREATE A CAR AND RUN
car = carSprite('sprites/car_orange.png', (60, 60))
cones = [
    coneSprite((200, 200)),
    coneSprite((600, 200)),
    coneSprite((600, 400)),
    coneSprite((200, 400))
]
car_group = pygame.sprite.RenderPlain(car)
cones_group = pygame.sprite.RenderPlain(cones)

while 1:
    # USER INPUT
    deltat = clock.tick(tick_rate)
    for event in pygame.event.get():
        if hasattr(event, 'key'):
            down = event.type == KEYDOWN
            if event.key == K_RIGHT: car.k_right = down * -5
            elif event.key == K_LEFT: car.k_left = down * 5
            elif event.key == K_UP: 
                car.k_up = down * 50
            elif event.key == K_DOWN: car.k_down = -1 * down * 50
            elif event.key == K_SPACE: car.k_space = down * 5
            elif event.key == K_ESCAPE: 
                pauseMenu('user')
            elif event.key == K_RETURN: 
                for cone in cones: cone.update(False)
                print current_car
                car = carSprite('sprites/car_' + colours[current_car] + '.png', (60, 60))
                car_group = pygame.sprite.RenderPlain(car)
            elif event.key == K_c: 
                current_car += 1
                if current_car > 4: current_car = 0
                car.change(current_car)
                
    # Draw the scene
    
    for cone in cones:
        if car.rect.colliderect(cone): cone.update(True)
        
    screen.blit(background, (0, 0))
    
    cones_group.draw(screen)
    car_group.update(deltat)
    car_group.draw(screen)
    pygame.display.flip()
    
    
    
    
    
    
    
    
    
    