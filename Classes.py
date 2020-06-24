import pygame
import os
import math
import random
from pygame.mask import from_surface
import MathPrograms

w = 1300
h = 550
screen = pygame.display.set_mode((w, h))

pygame.init()
curdir = os.path.dirname(os.path.realpath(__file__))
os.chdir(curdir)

events = pygame.event.get()
pressed = pygame.key.get_pressed()
mousestats = pygame.mouse.get_pressed()
fps = 60
items = []
selects = []
structbuildtimes = {}
structbuildtimes['TownCenter'] = 10
structwidths = {}
structwidths['TownCenter'] = int((screen.get_width())*(250/2400))
structheights = {}
structheights['TownCenter'] = int((screen.get_height())*(250/1100))

pygame.mouse.set_visible(False)
#colors
green = (0, 255, 0)
darkgreen = (0, 138, 0)

red = (255, 0, 0)
darkred = (138, 0, 0)

blue = (0, 0, 255)
darkblue = (0, 0, 138)

purple = (160, 0, 255)
darkpurple = (78, 0, 127)

paleyellow = (255, 255, 50)
darkyellow = (138, 138, 0)
brightyellow = (255, 255, 0)

turquoise = (0, 255, 255)
darkturquoise = (0, 138, 138)

orange = (255, 128, 0)
darkorange = (138, 69, 0)

backgroundcolor = (48, 5, 128)

class Player(object):
    def __init__(self, color, color2, x, y, screen, race = None):
        global items
        self.x = x
        self.y = y
        self.race = race.lower()
        self.screen = screen
        self.clickattack = False
        self.width = int((self.screen.get_width())*(60/2400))
        self.height = int((self.screen.get_height())*(66/1100))
        self.startx = int((self.screen.get_width() - ((self.screen.get_width()) * (250/2400)))/2)
        self.starty = int((self.screen.get_height() - ((self.screen.get_height()) * (250/2400)))/2)
        self.villx = int(self.startx - 2)
        self.villy = int(self.starty + ((self.screen.get_height())*(250/2400)) + 2)
        self.color = color
        self.color2 = color2
        self.cursoroffx = 0
        self.cursoroffy = 0

        if (self.race == "human") or (not self.race):
            self.cursor = pygame.transform.scale(pygame.image.load('BasicCursor.png'), (self.width, self.height))
        elif self.race in ['tzi', 'purist']:
            self.cursor = pygame.transform.scale(pygame.image.load('CyrackCursor.png'), (self.width, self.height))
        self.startcursor = self.cursor

        self.reticle = pygame.transform.scale(pygame.image.load('MouseOverCursor.png'), (self.width, self.height))

        self.StartingCenter = TownCenter(self.startx, self.starty, self.screen, race = self.race, player = self)
        items.append(self.StartingCenter)
        for i in range(5):
            items.append(Worker(self.villx, self.villy, self.screen, race = self.race, player = self))

    def draw(self):
        global items
        for item in items:
            item.draw()
        self.screen.blit(self.cursor, (self.x-self.cursoroffx, self.y-self.cursoroffy))
        self.CursorMask = pygame.mask.from_surface(self.cursor)
        

    def update(self, events, mousestats = None, pressed = None):
        global items
        global selects
        self.x, self.y = pygame.mouse.get_pos()
        for item in items:
            item.rect = pygame.Rect(item.x,item.y,item.width,item.height)
            #print(item,item.rect)
            item.Pmx = self.x - item.rect.x
            item.Pmy = self.y - item.rect.y
            #print("coords:",item.Pmx,item.Pmy,self.x,self.y,item.rect.collidepoint(self.x, self.y))
            c = item.rect.collidepoint(self.x, self.y)
            #if c:
            #    print(item,c,item.mask.get_at((item.Pmx, item.Pmy)))


            if (item.rect.collidepoint(*(self.x, self.y))) and item.mask.get_at((item.Pmx, item.Pmy)):
                #print("Moused over:",item)
                item.mousedover = True
            else:
                item.mousedover = False
            item.update(events, mousestats, pressed)
            if item.mousedover:
                self.cursor = self.reticle
                self.cursoroffx = int(self.width / 2)
                self.cursoroffy = int(self.height / 2)
            else:
                self.cursor = self.startcursor
                self.cursoroffx = 0
                self.cursoroffy = 0


class Worker(object):
    def __init__(self, x, y, screen, race = None, player = None):
        self.x = x
        self.y = y
        self.race = player.race.lower()
        self.player = player
        self.screen = screen
        self.width = int((self.screen.get_width())*(60/2400))
        self.height = int((self.screen.get_height())*(66/1100))
        self.buildingtime = 0
        self.truebuildingtime = 0
        self.buildX, self.buildY = self.x, self.y
        self.searchingtobuild = False
        self.structwidth, self.structheight = structwidths['TownCenter'], structheights['TownCenter']
        self.structure = TownCenter
        self.center = int(self.x + (self.width)/2), int(self.y + (self.height)/2)
        self.ismoving = False
        self.dx = 0
        self.dy = 0
        self.traveldist = MathPrograms.PythagHyp(self.dx, self.dy)
        self.selected = False
        self.mousedover = False
        self.HPMAX = 50
        self.hitpoints = self.HPMAX
        self.ATKDAM = 5
        self.TRUEDAM = 5

        if (self.race == "human"):
            self.face = pygame.transform.scale(pygame.image.load('ICM.png'), (self.width, self.height))
            self.font = pygame.font.SysFont("Calibri Bold", 60)
            self.SHIELDMAX = 0
            self.armor = 5
            self.movespeed = 3.94
        elif self.race == 'tzi':
            self.face = pygame.transform.scale(pygame.image.load('BotMaker.png'), (self.width, self.height))
            self.font = pygame.font.SysFont("Trebuchet MS Bold", 60)
            self.armor = 10
            self.movespeed = 3.94
            self.SHIELDMAX = 25
        elif self.race == 'purist':
            self.face = pygame.transform.scale(pygame.image.load('VoidCrafter.png'), (self.width, self.height))
            self.font = pygame.font.SysFont("Verdana Bold", 60)
            self.armor = 2
            self.movespeed = 5
            self.SHIELDMAX = 10
        
        self.mask = pygame.mask.from_surface(self.face)
        self.shields = self.SHIELDMAX
        self.ATKRANGE = self.movespeed
        self.isattacking = False
        self.ATKRESETMAX = fps
        self.ATKRESET = self.ATKRESETMAX
        
        self.selectedtext = self.font.render("Worker Selected", True, blue)
        self.buildcounter = self.font.render("%d"%self.truebuildingtime, True, purple)
        self.selectedtextx = int((self.screen.get_width()/2) - (self.selectedtext.get_width()/2))
        self.selectedtexty = int((self.screen.get_height() * 15/1100))
        self.healthcounter = pygame.font.SysFont("Arial", 10).render(("%d"%self.hitpoints + "/" + "%d"%self.HPMAX), True, red)

    def moveXY(self, x, y):
        self.dx = x - self.x
        self.dy = y - self.y
        self.traveldist = MathPrograms.PythagHyp(self.dx, self.dy)
        if self.traveldist != 0:
            self.x += (self.dx * self.movespeed)/self.traveldist
            self.y += (self.dy * self.movespeed)/self.traveldist
        if self.traveldist <= self.movespeed:
            x, y = self.x, self.y
            self.ismoving = False

    def attack(self, target):
        self.moveXY(target.x, target.y)
        #play an attacking animation
        if MathPrograms.PythagHyp(target.x - self.x, target.y - self.y) <= self.ATKRANGE:
            self.ismoving = False
            self.ATKRESET = 0
            self.TRUEDAM = self.ATKDAM * ((100 - target.armor)/100)
            if target.shields <= self.TRUEDAM:
                target.shields = 0
                target.hitpoints -= (self.TRUEDAM - target.shields)
            else:
                target.shields -= self.TRUEDAM
        self.isattacking = False

    def draw(self):
        if self.mousedover:
            pygame.draw.rect(self.screen, self.player.color2, (int(self.x - 1), int(self.y - 1), int(self.width + 2), int(self.height + 2)), 2)
        if self.selected:
            pygame.draw.circle(self.screen, self.player.color, self.center, int((self.height)/2), 1)
        self.screen.blit(self.face, (int(self.x), int(self.y)))
        if self.hitpoints < self.HPMAX:
            screen.blit(self.healthcounter,
                (int(self.x + (self.width/2) - (self.healthcounter.get_width()/2)), int(self.y - self.healthcounter.get_height() - 2)))
        self.mask = pygame.mask.from_surface(self.face)

    def build(self, structure, buildtime):
        global items
        if self.race == 'human':
            self.moveXY(self.buildX + self.structwidth + 2, self.buildY + self.structheight + 2)
        self.buildingtime += 1
        self.truebuildingtime = int(self.buildingtime/fps)
        self.buildcounter = self.font.render("%d"%self.truebuildingtime, True, purple)
        screen.blit(self.buildcounter,
            (int(self.buildX + (((self.screen.get_width())*70/2400) - self.buildcounter.get_height()/2)), int(self.buildY - (((self.screen.get_height())*(70/1100)) - self.buildcounter.get_height()/2))))
        if self.buildingtime >= buildtime*fps:
            self.buildingtime = 0
            items.append(structure(int(self.buildX), int(self.buildY), self.screen, self.race, self.player))

    def update(self, events, mousestats = None, pressed = None):
        global selects
        global items
        if self.selected and (pressed[pygame.K_BACKSPACE] or pressed[pygame.K_DELETE]):
            self.hitpoints -= self.HPMAX
        if self.hitpoints <= 0:
            items.remove(self)
        self.healthcounter = pygame.font.SysFont("Arial", 10).render(("%d"%self.hitpoints + "/" + "%d"%self.HPMAX), True, red)
        self.center = int(self.x + (self.width)/2), int(self.y + (self.height)/2)
        if self.mousedover and mousestats[0]:
            selects = []
            selects.append(self)
        else:
            selects = selects
        if self in selects:
            self.selected = True
            #print(self.selectedtextx, self.selectedtexty)
            screen.blit(self.selectedtext,
                (int(self.selectedtextx), int(self.selectedtexty)))
        else:
            self.selected = False
        if ((self.selected) and (pressed[pygame.K_t])):
            self.structure = TownCenter
            self.time2build = structbuildtimes['TownCenter']
            self.structwidth, self.structheight = structwidths['TownCenter'], structheights['TownCenter']
            self.searchingtobuild = True
        '''
        if self.searchingtobuild:
            self.player.cursor = pygame.transform.scale(pygame.image.load('CrossHair.png'), (self.player.width, self.player.height))
        else:
            self.player.cursor = self.player.startcursor
        '''
        if self.searchingtobuild and mousestats[0]:
            self.searchingtobuild = False
            self.buildX, self.buildY = int(self.player.x - ((self.screen.get_width())*(70/2400))), int(self.player.y - ((self.screen.get_height())*(70/1100)))
            self.build(self.structure, self.time2build)
        elif (self.buildingtime > 0) and (self.buildingtime < self.time2build * fps):
            self.build(self.structure, self.time2build)
        #if self.selected:
            #self.debugtext = self.font.render(mousestats.__repr__(), True, blue)
            #screen.blit(self.debugtext,(200, 100))
        
        for item in items:
            if self.selected and mousestats[2] and item.mousedover and (self.ATKRESET >= self.ATKRESETMAX):
                self.target = item
                self.isattacking = True
            elif self.selected and mousestats[2]:
                self.ismoving = True
                self.moveX = self.player.x
                self.moveY = self.player.y

        if self.isattacking:
            self.attack(self.target)
        else:
            if self.ismoving:
                self.moveXY(self.moveX, self.moveY)
            self.ATKRESET += 1

class TownCenter(object):
    def __init__(self, x, y, screen, race = None, player = None):
        self.x = int(x)
        self.y = int(y)
        self.player = player
        self.race = self.player.race.lower()
        self.screen = screen
        self.width = int((self.screen.get_width())*(250/2400))
        self.height = int((self.screen.get_height())*(250/1100))
        self.training = 0
        self.showtraining = 0
        self.selected = False
        self.mousedover = False
        self.center = int(self.x + (self.width)/2), int(self.y + (self.height)/2)
        self.trainX, self.trainY = self.x - 2, self.y - 2

        if self.race == "human":
            self.face = pygame.transform.scale(pygame.image.load('PlanetaryOutpost.png'), (self.width, self.height))
            self.font = pygame.font.SysFont("Calibri Bold", 60)
            self.HPMAX = 1200
            self.SHIELDMAX = 0
            self.armor = 10
        elif self.race == 'tzi':
            self.face = pygame.transform.scale(pygame.image.load('CyberSphere.png'), (self.width, self.height))
            self.font = pygame.font.SysFont("Trebuchet MS Bold", 60)
            self.HPMAX = 1500
            self.SHIELDMAX = 700
            self.armor = 25
        elif self.race == 'purist':
            self.face = pygame.transform.scale(pygame.image.load('VoidTemple.png'), (self.width, self.height))
            self.font = pygame.font.SysFont("Verdana Bold", 60)
            self.HPMAX = 2000
            self.SHIELDMAX = 100
            self.armor = 20

        self.hitpoints = self.HPMAX
        self.shields = self.SHIELDMAX

        self.mask = pygame.mask.from_surface(self.face)

        self.selectedtext = self.font.render("Base Selected", True, blue)
        self.selectedtextx = int((self.screen.get_width()/2) - (self.selectedtext.get_width()/2))
        self.selectedtexty = int((self.screen.get_height() * 15/1100))
        self.healthcounter = pygame.font.SysFont("Arial", 20).render(("%d"%self.hitpoints + "/" + "%d"%self.HPMAX), True, red)
        #self.kind = 'TownCenter'


    def draw(self):
        if self.mousedover:
            pygame.draw.rect(self.screen, self.player.color2, (int(self.x - 1), int(self.y - 1), int(self.width + 2), int(self.height + 2)), 2)
        if self.selected:
            pygame.draw.circle(self.screen, self.player.color, self.center, int((self.height)/2), 1)
        self.screen.blit(self.face, (self.x, self.y))
        if self.hitpoints < self.HPMAX:
            screen.blit(self.healthcounter,
                (int(self.x + (self.width/2) - (self.healthcounter.get_width()/2)), int(self.y - self.healthcounter.get_height() - 2)))
        self.mask = pygame.mask.from_surface(self.face)
    
    def update(self, events, mousestats = None, pressed = None):
        global items
        global selects
        if self.selected and (pressed[pygame.K_BACKSPACE] or pressed[pygame.K_DELETE]):
            self.hitpoints -= self.HPMAX
        if self.hitpoints <= 0:
            items.remove(self)
        self.healthcounter = pygame.font.SysFont("Arial", 20).render(("%d"%self.hitpoints + "/" + "%d"%self.HPMAX), True, red)
        if self.mousedover and mousestats[0]:
            selects = []
            selects.append(self)
        else:
            selects = selects
        if self in selects:
            self.selected = True
            screen.blit(self.selectedtext,
                (int(self.selectedtextx), int(self.selectedtexty)))
        else:
            self.selected = False            
        
        if self.selected and mousestats[2]:
            self.trainX, self.trainY = pygame.mouse.get_pos()

        if ((self.selected == True) and (pressed[pygame.K_c])) or ((self.training > 0) and (self.training < 12 * fps)):
            self.training += 1
            self.showtraining = int(self.training/fps)
            if self.training >= 12*fps:
                self.training = 0
                newvillager = Worker(self.x, self.y, screen, race = self.race, player = self.player)
                items.append(newvillager)
                newvillager.moveX, newvillager.moveY = self.trainX, self.trainY
                newvillager.ismoving = True
            self.text = self.font.render("%d"%self.showtraining, True, brightyellow)
            self.traintimerx = int(self.x + ((self.width // 2) - (self.text.get_width()/ 2)))
            self.traintimery = int(self.y + ((self.height // 2) - (self.text.get_height() // 2)))
            screen.blit(self.text,
                (self.traintimerx, self.traintimery))