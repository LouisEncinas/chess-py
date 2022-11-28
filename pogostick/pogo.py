import sys
import pygame
import math
import copy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
POGO_WIDTH = 10
POGO_HEIGHT = 80

class Vector2D:

    def __init__(self, tpl:tuple[int,int]) -> None:
        self.tuple = tpl
        self.list = list(tpl)
        self.x = tpl[0]
        self.y = tpl[1]

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __neg__(self):
        return Vector2D((-self.x,-self.y))

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
    OTHER = 'other'
    LIST = [RIGHT, LEFT, BOTTOM, TOP]

def collide_rect_rect(r1:pygame.Rect, r2:pygame.Rect):
    if (r1.left < r2.right) and (r1.right > r2.left) and (r1.top < r2.bottom) and (r1.bottom > r2.top):
        lst = [abs(r2.right - r1.left), abs(r2.left - r1.right), abs(r2.bottom - r1.top), abs(r2.top - r1.bottom)]
        index = lst.index(min(lst))
        return Collision.LIST[index]
    return Collision.NONE

def collide_circle_rect(c:Circle, r:pygame.Rect) -> tuple[str,Vector2D]:
    theta = math.atan2(c.center.y - r.center[1], c.center.x - r.center[0])
    point = Vector2D((c.center.x - math.cos(theta) * c.radius, c.center.y - math.sin(theta) * c.radius))
    if (r.left <= point.x <= r.right) and (r.top <= point.y <= r.bottom):
        lst = [abs(r.right - point.x), abs(r.left - point.x), abs(r.bottom - point.y), abs(r.top - point.y)]
        copy_lst = copy.deepcopy(lst)
        copy_lst.remove(min(copy_lst))
        if min(copy_lst) <= 5:
            return Collision.OTHER, point
        return Collision.LIST[lst.index(min(lst))], point
    return Collision.NONE, point

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
img = pygame.image.load('img/louisboy.png').convert()
img = pygame.transform.scale(img, (SCREEN_HEIGHT*.1,SCREEN_HEIGHT*.1))
speed = [2,2]
img_rect = img.get_rect()
img_rect.y += 10
img_circle = Circle(Vector2D(img_rect.center), img_rect.size[0]/2)

OBS_WIDTH = 100
OBS_HEIGHT = 100
obstacle = pygame.Rect((SCREEN_WIDTH - OBS_WIDTH)/2, (SCREEN_HEIGHT - OBS_HEIGHT)/2, OBS_WIDTH, OBS_HEIGHT)

invicible_frame = 0
invicible = False
lst_collisions:list[Circle] = []
        
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    img_rect = img_rect.move(speed)
    img_circle.move(speed)
    if img_rect.left < 0 or img_rect.right > SCREEN_WIDTH:
        speed[0] = -speed[0]
    if img_rect.top < 0 or img_rect.bottom > SCREEN_HEIGHT:
        speed[1] = -speed[1]

    collision, collision_point = collide_circle_rect(img_circle, obstacle)
    if collision != Collision.NONE and not invicible:
        invicible = True
        lst_collisions.append(Circle(Vector2D(collision_point.tuple), 5))
        if collision == Collision.LEFT or collision == Collision.RIGHT:
            speed[0] = -speed[0]
        if collision == Collision.TOP or collision == Collision.BOTTOM:
            speed[1] = -speed[1]
        if collision == Collision.OTHER:
            speed[0] = -speed[0]
            speed[1] = -speed[1]

    if invicible:
        if invicible_frame < 10:
            invicible_frame += 1
        else:
            invicible = False
            invicible_frame = 0

    clock.tick(60)
    screen.fill((0,0,0))
    screen.blit(img, img_rect)
    pygame.draw.rect(screen, (0,0,255), obstacle)
    for collision in lst_collisions:
        pygame.draw.circle(screen, (255,0,0), collision.center.tuple, collision.radius)

    pygame.display.update()