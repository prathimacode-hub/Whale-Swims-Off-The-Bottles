import pygame, sys, random
from object_classes import *
from interaction import interaction
from check_collision import check_collision
import numpy as np

pygame.init()
font = pygame.font.SysFont("monospace", 15)
font_top = pygame.font.SysFont("monospace", 30)
SCREENSIZE = SCREENWIDTH, SCREENHEIGHT = 288, 512

bg_island_str = "images/bg_island.png"
bg_island = pygame.image.load(bg_island_str)
plankett = "images/finish_game_screen.png"
scrollbar_str = "images/scrolling_bar.png"; scrollbar_split_str = "images/scrolling_bar_split.png"
whale1down = "images/whale_1_down.png"; whale2down = "images/whale_2_down.png"; whale3down = "images/whale_3_down.png"
whale1for = "images/whale_1_for.png"; whale2for = "images/whale_2_for.png"; whale3for = "images/whale_3_for.png"
whale1up = "images/whale_1_up.png"; whale2up = "images/whale_2_up.png"; whale3up = "images/whale_3_up.png"
whale_dead = "images/whale_dead.png"; bubble = "images/bubble.png"
cola = "images/cola.png"; boat = "images/boat.png"

down = [whale1down, whale2down, whale3down]
forward = [whale1for, whale2for, whale3for]
up = [whale1up, whale2up, whale3up]

screen = pygame.display.set_mode(SCREENSIZE)
pygame.display.set_caption("Swimming Whale! :>")

clock = pygame.time.Clock()
FPS = 30
total_frames = 0
obstaclespeed = 5
seconds = 0
state = "running"

score = 0      #Number of obstacles passed
best = 0  #Highest score so far while running game

fish = Fish(int(SCREENWIDTH*0.2), int(SCREENHEIGHT*0.2)+ 100, down, forward, up, FPS, whale_dead)
bar = ScrollBar(scrollbar_str)
standingstillbar = ScrollBar(scrollbar_str, 0, 0, 96, True)
endgame = EndGameScreen(plankett)

while True:
    screen.blit(bg_island, [0,0]) #Draw background

    score = interaction(fish, state, FPS, scrollbar_str, score)      #Handle user input returns current score

    standingstillbar.draw(screen)
    for bars in ScrollBar.BarList:
        bars.update()
        bars.draw(screen)
        bars.slow_down(fish.time_dead, fish.alive)
        ScrollBar.BarList = [bar for bar in ScrollBar.BarList if not bar.rect.left < -bar.rect.width]
        if len(ScrollBar.BarList) == 1 and ScrollBar.BarList[0].rect.left < -bars.rect.width + SCREENWIDTH:
            ScrollBar(scrollbar_str, bars.rect.left + bars.rect.width, -ScrollBar.BarList[0].vx)
    obstaclespeed = -ScrollBar.BarList[0].vx #Update speed so its the same for all obstacles (same as scrollbar)

    Bubble.BubbleList = [elem for elem in Bubble.BubbleList if elem.rect.left > -elem.rect.width]
    for bubble in Bubble.BubbleList:
        bubble.update(obstaclespeed)
        bubble.draw(screen)

    if total_frames % FPS == 0 and fish.alive: #Spawn something every second...
        Obstacle(obstaclespeed, SCREENWIDTH)

    if total_frames % (2*FPS) == 0 and fish.alive:
        Bubble(SCREENWIDTH)

    fish.update(total_frames)     #Update fish position and state

    if fish.alive:
        check_collision(fish, Obstacle.ObstacleList, Bubble.BubbleList, 0.9) # If there is a collision, fish dies

    for obstacle in Obstacle.ObstacleList:
        Obstacle.ObstacleList = [elem for elem in Obstacle.ObstacleList if not elem.rect.left < -elem.rect.width]
        obstacle.set_speed(obstaclespeed)
        obstacle.update(fish.rect.top)
        obstacle.draw(screen)

    fish.draw(screen)
    for bars in ScrollBar.BarList:
        bars.draw_half(screen)

    best = endgame.check_if_hightscore(best, score, fish.endgame)
    endgame.draw(screen, fish.endgame, font, score, best)
    fish.draw_oxygentime(screen, font)

    #------------------------------------------
    # Blits score to screen
    text = font_top.render(str(score),1,(0,0,0))
    text_rect = text.get_rect()
    textpos = (SCREENWIDTH*0.5 - text_rect.width*0.5, 20)
    screen.blit(text,textpos)
    #------------------------------------------

    pygame.display.update()

    clock.tick(FPS)
    if fish.alive:
        score += 10
    total_frames += 1
    if total_frames % FPS == 0:
        seconds += 1
