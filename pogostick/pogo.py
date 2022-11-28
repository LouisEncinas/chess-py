import sys
import pygame
import math

WIDTH = 600
HEIGHT = 480
P4 = math.pi/4

class Vector2D:

    def __init__(self, tpl:tuple[int,int]) -> None:
        self.tuple = tpl
        self.x = tpl[0]
        self.y = tpl[1]

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

class Circle:

    def __init__(self, center:Vector2D, radius:int) -> None:
        self.center = center
        self.radius = radius
        self.left = self.center.x - self.radius
        self.right = self.center.x + self.radius
        self.bottom = self.center.y - self.radius
        self.top = self.center.y + self.radius

    def move(self, tpl:tuple[int,int]):
        self.center.x += tpl[0]
        self.center.y += tpl[1]
        self.left = self.center.x - self.radius
        self.right = self.center.x + self.radius
        self.bottom = self.center.y - self.radius
        self.top = self.center.y + self.radius

    def getCenter(self) -> tuple[int,int]:
        return self.center.tuple

class Collision:

    NONE = 'none'
    TOP = 'top'
    BOTTOM = 'bottom'
    LEFT = 'left'
    RIGHT = 'right'
    LIST = [RIGHT, LEFT, BOTTOM, TOP]

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
img = pygame.image.load('img/louisboy.png').convert()
img = pygame.transform.scale(img, (HEIGHT*.4,HEIGHT*.4))
speed = [2,2]
img_rect = img.get_rect()
img_circle = Circle(Vector2D(img_rect.center), img_rect.size[0]/2)

OBS_WIDTH = 20
OBS_HEIGHT = 20
obstacle = pygame.Rect((WIDTH - OBS_WIDTH)/2, (HEIGHT - OBS_HEIGHT)/2, OBS_WIDTH, OBS_HEIGHT)

def collide_rect_rect(r1:pygame.Rect, r2:pygame.Rect):
    if (r1.left < r2.right) and (r1.right > r2.left) and (r1.top < r2.bottom) and (r1.bottom > r2.top):
        lst = [abs(r2.right - r1.left), abs(r2.left - r1.right), abs(r2.bottom - r1.top), abs(r2.top - r1.bottom)]
        index = lst.index(min(lst))
        return Collision.LIST[index]
    return Collision.NONE

def collide_circle_rect(c:Circle, r:pygame.Rect):
    theta = math.atan2(c.center.y - r.center[1], c.center.x - r.center[0])
    point = Vector2D((c.center.x - math.cos(theta) * c.radius, c.center.y - math.sin(theta) * c.radius))
    if (r.left <= point.x <= r.right) and (r.top <= point.y <= r.bottom):
        if P4 < theta < 3*P4:
            return Collision.BOTTOM 
        elif -P4 < theta < P4:
            return Collision.RIGHT
        elif -3*P4 < theta < -P4:
            return Collision.TOP
        else:
            return Collision.LEFT
    return Collision.NONE
        
while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    img_rect = img_rect.move(speed)
    img_circle.move(speed)
    if img_rect.left < 0 or img_rect.right > WIDTH:
        speed[0] = -speed[0]
    if img_rect.top < 0 or img_rect.bottom > HEIGHT:
        speed[1] = -speed[1]
    collision = collide_circle_rect(img_circle, obstacle)
    if collision != Collision.NONE:
        if collision == Collision.LEFT or collision == Collision.RIGHT:
            speed[0] = -speed[0]
        if collision == Collision.TOP or collision == Collision.BOTTOM:
            speed[1] = -speed[1]

    clock.tick(60)
    screen.fill((0,0,0))
    screen.blit(img, img_rect)
    pygame.draw.rect(screen, (0,0,255), obstacle)

    pygame.display.update()