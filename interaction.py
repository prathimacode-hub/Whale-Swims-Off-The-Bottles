import pygame, sys
from object_classes import *

def interaction(fish, state, FPS, scrollbar_str, score):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            fish.moveup()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            fish.movedown()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            fish.restart(FPS)
            Obstacle.ObstacleList = []
            ScrollBar.BarList = []
            Bubble.BubbleList = []
            bar = ScrollBar(scrollbar_str)
            standingstillbar = ScrollBar(scrollbar_str, 0, 0, 96, True)
            score = 0

        """
        ADD:
        - Screenshot?
        - Pause button?
        """
    return score
