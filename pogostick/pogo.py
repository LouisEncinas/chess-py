import sys
import pygame
import math
import copy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
POGO_LENGTH = 80

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

    def __add__(self, vec):
        return Vector2D((self.x + vec.x, self.y + vec.y))

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

class Block:

    def __init__(self, position:Vector2D, size:Vector2D) -> None:
        self.hitbox:pygame.Rect = pygame.Rect(position.x, position.y, size.x, size.y)
        self.color = (0,100,0)
        self.colideable = True
        self.under_gravity = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)

class Player:

    def __init__(self, position:Vector2D) -> None:
        self.body:pygame.Rect = pygame.Rect(position.x, position.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.pogo_point:Vector2D = Vector2D((position.x + PLAYER_WIDTH/2, position.y + PLAYER_HEIGHT/2 + POGO_LENGTH))
        self.body_color = (240,235,210)
        self.pogo_color = (121, 19, 48)
        self.colideable = True
        self.under_gravity = True
        self.speed = Vector2D((0,0))

    def update(self, delta_time, gravity):
        self.speed.y += delta_time*gravity
        self.move(self.speed)

    def move(self, vec:Vector2D):
        self.body = self.body.move(vec.x, vec.y)
        self.pogo_point = self.pogo_point + vec
        # move doesn't change body pos
        # move pogo point

    def collide(self, lst:list[pygame.Rect]):
        for hitbox in lst:
            if hitbox.left < self.pogo_point.x < hitbox.right and hitbox.top < self.pogo_point.y < hitbox.bottom:
                pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.body_color, self.body)
        pygame.draw.line(screen, self.pogo_color, self.body.center, self.pogo_point.tuple)

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
frame_rate = 60
delta_time = 1/frame_rate
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player = Player(position=Vector2D(((SCREEN_WIDTH - PLAYER_WIDTH)/2, (SCREEN_HEIGHT - PLAYER_HEIGHT)/2)))
floor = Block(Vector2D((0,SCREEN_HEIGHT - 100)), Vector2D((SCREEN_WIDTH, 100)))
        
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    player.update(delta_time, 10)

    clock.tick(frame_rate)
    screen.fill((0,0,0))
    player.draw(screen)
    floor.draw(screen)

    pygame.display.update()