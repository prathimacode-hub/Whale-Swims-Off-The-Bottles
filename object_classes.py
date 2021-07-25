import pygame, sys, random
import numpy as np

class ScrollBar:
    BarList = []
    def __init__(self, img_str, x = 0, vx = 5, y = 96, standingstill = False):
        self.image = pygame.image.load(img_str)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.vx = -vx

        self.starting_vx = self.vx
        self.starting_rect = self.rect

        if standingstill:
            pass
        else:
            ScrollBar.BarList.append(self)

        self.image_half = self.image.subsurface(0,21,self.rect.width, 19)

    def update(self):
        self.rect.left += self.vx

    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))

    def draw_half(self,screen):
        screen.blit(self.image_half, (self.rect.left, self.rect.top + 0.5*self.rect.height + 1))

    def slow_down(self, frames_dead, fish_alive):
        if self.vx < 0 and frames_dead % 18 == 0 and not fish_alive:
            self.vx += 1


class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y, down, forward, up, FPS, dead_img):
        pygame.sprite.Sprite.__init__(self)

        self.FPS = FPS
        self.oxygentime = 15
        self.oxygentime_in_seconds = self.oxygentime

        self.img_down = []; self.img_forward = []; self.img_up = []
        for i in range(len(down)):
            self.img_down.append(pygame.image.load(down[i]))
            self.img_forward.append(pygame.image.load(forward[i]))
            self.img_up.append(pygame.image.load(up[i]))
        self.dead_img = pygame.image.load(dead_img)

        self.vy = 0
        self.movetimer = 0 #Kan brukes til aa begrense brukers mulighet til aa spamtrykke...

        self.imagetimer = 0
        self.image_index = 0
        self.image_counting_up = True

        self.oxygentimer = FPS*self.oxygentime #Total amount of frames in 20 secs
        self.starting_otime = self.oxygentimer

        self.image = self.img_down[self.image_index]

        self.rect = self.image.get_rect()
        self.rect.left = x; self.rect.top = y
        self.start_y = y

        self.alive = True
        self.time_dead = 0
        self.endgame = False

    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))

    def draw_oxygentime(self, screen, font, colornormal = (0,0,0), colorcritical = (255,0,0)):
        if self.oxygentime_in_seconds >= self.oxygentime/3.:
            label = font.render(str(self.oxygentime_in_seconds),1,colornormal)
        else:
            label = font.render(str(self.oxygentime_in_seconds),1,colorcritical)

        screen.blit(label, (250,480))

    def update(self, total_frames):
        self.imagetimer += 1
        if self.rect.top < 115 and self.alive: #Hvis over vannet og i live, reset timer
            self.oxygentimer = self.FPS*self.oxygentime
        if self.alive:
            self.oxygentimer -= 1
            self.oxygentime_in_seconds = int(round(self.oxygentimer/self.FPS))
        if self.oxygentimer <= 0: #Hvis tom for oksygen, die
            self.alive = False
        elif self.oxygentimer > self.starting_otime:
            self.oxygentimer = self.starting_otime

        if abs(self.vy) > 2: #Bremsing
            self.vy = (0.92*self.vy)
        else:
            self.vy = int(0.99*self.vy)
        self.rect.top += self.vy

        if self.rect.top < 110: #Kollisjon med vannoverflate
            self.vy = 0
            self.rect.top = 110
        if self.rect.top > 512-self.rect.height: #Kollisjon med bunnen av skjermen
            self.vy = 0
            self.rect.top = 512-self.rect.height

        if self.alive:
            if self.imagetimer % 10 == 0: #Update sprite index every 10 frames
                if self.image_index == 0:
                    self.image_index = 1
                    self.image_counting_up = True
                elif self.image_index == 1 and self.image_counting_up:
                    self.image_index = 2
                    self.image_counting_up = False
                elif self.image_index == 2 and not self.image_counting_up:
                    self.image_index = 1
                elif self.image_index == 1 and not self.image_counting_up:
                    self.image_index = 0

            if self.rect.top < 220: #Eye direction depends on y position
                self.image = self.img_down[self.image_index]
            elif 200 < self.rect.top < 360:
                self.image = self.img_forward[self.image_index]
            elif self.rect.top > 360:
                self.image = self.img_up[self.image_index]
        else:
            self.image = self.dead_img


        if self.alive:
            pass
        else:
            self.time_dead += 1
            if self.time_dead > 3*self.FPS:
                self.endgame = True
                self.image = pygame.transform.flip(self.image, False, True)
                if self.time_dead % 3 == 0:
                    self.vy -= 2

    def moveup(self):
        if self.alive:
            self.vy -= 10
        else:
            pass

    def movedown(self):
        if self.alive:
            self.vy += 10
        else:
            pass

    def restart(self, FPS): #Resets bird instance to starting position and values
        self.vy = 0
        self.rect.top = self.start_y
        self.alive = True
        self.time_dead = 0
        self.movetimer = 0
        self.oxygentimer = FPS*self.oxygentime
        self.endgame = False

    def get_collisionrect(self, scalefactor):  #Inflates rectangle around center by a factor of the argument
        w = round(self.rect.width*scalefactor); x = self.rect.left + round(self.rect.width*scalefactor*0.5)
        h = round(self.rect.height*scalefactor); y = self.rect.top + round(self.rect.height*scalefactor*0.5)
        return pygame.Rect(x, y, w, h)

class Obstacle:
    ObstacleList = []
    def __init__(self, speed, SCREENWIDTH, specific_obstacle = None):
        """
        Obstacle types and starting y values.
        cola : y = 300 +- 50. Movement: sin -> self.rect.top = self.starting_y + int(round(10*np.sin(self.random_number*2*np.pi*self.frames_existed*0.02)))
        boat : y = ...
        Ship : y = ...
        Shark : y = ... Can track whale.
        -- Insert more obstacles here --
        """
        Obstacle.ObstacleList.append(self)

        if specific_obstacle == None:
            obstacle_types = ["cola", "boat", "shark", "ship"]
            self.obst = obstacle_types[random.randint(0,1)]
        else:
            self.obst = specific_obstacle

        self.image = pygame.image.load("images/" + self.obst + ".png")
        self.rect = self.image.get_rect()
        self.rect.left = SCREENWIDTH
        self.vx = speed
        self.frames_existed = 0

        # Starting y position and other special attributes
        if self.obst == "cola":
            self.rect.top = 300 + random.randint(-50,50)
            self.starting_y = self.rect.top
            self.random_number = random.random()
        elif self.obst == "boat":
            self.rect.top = 72
        elif self.obst == "ship":
            self.rect.top = 0
        elif self.obst == "shark":
            self.rect.top = random.randint()
            self.sharkspeed = 1

    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))

    def update(self, bird_y):
        self.frames_existed += 1
        if self.obst == "cola":
            self.rect.top = self.starting_y + int(round(10*np.sin(self.random_number*2*np.pi*self.frames_existed*0.02))) # Change y pos
            self.rect.left -= self.vx
        elif self.obst == "boat":
            self.rect.left -= 2*self.vx
        elif self.obst == "ship":
            self.rect.left -= self.vx
        elif self.obst == "shark":
            self.rect.left -= self.vx
            if self.rect.top > bird_y:
                self.rect.top -= self.sharkspeed
            elif self.rect.top < bird_y:
                self.rect.top += self.sharkspeed

    def get_collisionrect(self, scalefactor):  #Inflates rectangle around center by a factor of the argument
        w = round(self.rect.width*scalefactor); x = self.rect.left + round(self.rect.width*scalefactor*0.5)
        h = round(self.rect.height*scalefactor); y = self.rect.top + round(self.rect.height*scalefactor*0.5)
        return pygame.Rect(x, y, w, h)

    def set_speed(self, speed):
        self.vx = speed

class Powerup:
    """
    -- Powerup ideas: --
    DOUBLE POINTS
    IMMUNITY + SUPER SPEED? (Inni ubaat f.eks)
    SMALLER WHALE SIZE?
    OXYGEN BOOST?

    -- Include bad powerups? --
    MOTSATT KNAPPER
    STORRE HVAL

    -- Include ?QUESTION MARK? powerup? --
    """
    PowerupList = []
    def __init__(self, SCREENWIDTH):
        self.rect.left = SCREENWIDTH
        self.rect.top = random.randint(250,480)

class Bubble:
    BubbleList = []
    def __init__(self, SCREENWIDTH, img_string = "images/bubble.png"):
        self.image = pygame.image.load(img_string)
        self.rect = self.image.get_rect()
        self.rect.left = SCREENWIDTH
        self.starting_y = random.randint(300,480)
        self.rect.top = self.starting_y
        self.oxygen_given = random.randint(2,5)

        self.popped = False
        Bubble.BubbleList.append(self)

    def update(self, vx):
        self.rect.left -= vx

    def draw(self, screen):
        if not self.popped:
            screen.blit(self.image, (self.rect.left, self.rect.top))



class EndGameScreen:
    def __init__(self, img_string, x = 44, y = 200):
        self.image = pygame.image.load(img_string)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.highscore_updated = False

    def draw(self, screen, showonscreen, font, score, best):
        if showonscreen:
            screen.blit(self.image, (self.rect.left, self.rect.top))

            scorelabel = font.render("Score : " + str(score),1,(0,0,0))
            screen.blit(scorelabel, (self.rect.left + 80, self.rect.top + 10))

            bestlabel = font.render("Best : " + str(best),1,(0,0,0))
            screen.blit(bestlabel, (self.rect.left + 80, self.rect.top + 30))

    def check_if_hightscore(self, best, current, endgame, screen = None, img_str = None):
        if current > best and endgame:
            best = current
        return best
