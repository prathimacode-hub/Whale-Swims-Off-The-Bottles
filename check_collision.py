import pygame, sys, random
from object_classes import *
import numpy as np

def check_collision(fish, obstaclelist, bubblelist, scalefactor, FPS = 30):
    for obstacle in obstaclelist:
        if fish.get_collisionrect(scalefactor).colliderect(obstacle.get_collisionrect(scalefactor)):
            fish.alive = False
    for bubble in bubblelist:
        if fish.rect.colliderect(bubble.rect) and fish.alive and not bubble.popped:
            fish.oxygentimer += bubble.oxygen_given*FPS
            bubble.popped = True
