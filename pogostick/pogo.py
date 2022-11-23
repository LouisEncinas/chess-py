import sys
import pygame

WIDTH = 600
HEIGHT = 480

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
img = pygame.image.load('img/louisboy.png').convert()
img = pygame.transform.scale(img, (HEIGHT*.4,HEIGHT*.4))
speed = [2,2]
img_rect = img.get_rect()

while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    img_rect = img_rect.move(speed)
    if img_rect.left < 0 or img_rect.right > WIDTH:
        speed[0] = -speed[0]
    if img_rect.top < 0 or img_rect.bottom > HEIGHT:
        speed[1] = -speed[1]

    clock.tick(60)
    screen.blit(img, img_rect)

    pygame.display.update()