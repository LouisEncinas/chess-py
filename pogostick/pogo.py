import sys
import pygame
import math

WIDTH = 600
HEIGHT = 480

class Vector2D:

    def __init__(self, tpl:tuple[int,int]) -> None:
        self.x = tpl[0]
        self.y = tpl[1]

    def getTuple(self) -> tuple[int,int]:
        return tuple((self.x, self.y))

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

    def getCenter(self) -> tuple[int,int]:
        return tuple((self.center.x, self.center.y))

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

def collide_circle_rect(screen, c:Circle, r:pygame.Rect):
    x_comp = c.center.x - r.center[0]
    y_comp = c.center.y - r.center[1]
    theta = math.atan2(y_comp, x_comp)
    point = Vector2D((c.center.x - math.cos(theta) * c.radius, c.center.y - math.sin(theta) * c.radius))
    pygame.draw.line(screen, (0,255,0), r.center, c.getCenter())
    pygame.draw.line(screen, (255,0,0), c.getCenter(), point.getTuple())

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
    # collision = collide(img_rect, obstacle)
    # if collision != Collision.NONE:
    #     if collision == Collision.LEFT or collision == Collision.RIGHT:
    #         speed[0] = -speed[0]
    #     if collision == Collision.TOP or collision == Collision.BOTTOM:
    #         speed[1] = -speed[1]

    clock.tick(60)
    screen.fill((0,0,0))
    screen.blit(img, img_rect)
    collide_circle_rect(screen, img_circle, obstacle)
    pygame.draw.rect(screen, (0,0,255), obstacle)

    pygame.display.update()