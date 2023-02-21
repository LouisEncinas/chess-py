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

def point_in_rect(point:Vector2D, r:pygame.Rect):
    if (r.left <= point.x <= r.right) and (r.top <= point.y <= r.bottom):
        lst = [abs(r.right - point.x), abs(r.left - point.x), abs(r.bottom - point.y), abs(r.top - point.y)]
        return Collision.LIST[lst.index(min(lst))]
    return Collision.NONE