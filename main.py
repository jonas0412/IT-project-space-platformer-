import json
import re
import math
import random
import os
import time
import sys
import pygame
from game import Game
from scripts.utils import load_image, load_images, Animation, load_stats, write_stats, center_text
from scripts.entities import PhysicsEntity , Player, Enemy
from scripts.tilemap import Tilemap
from scripts.sparks import Spark
from scripts.particles import Particle


class Menu:
    def __init__(self):
        pygame.mixer.pre_init()
        pygame.init()

        pygame.display.set_caption('space game')
        self.size1 = (640, 480)
        self.size2 = (640*2, 480*2)
        self.size = self.size1
        self.click = pygame.mixer.Sound('data/sfx/click.mp3')
        raw_array = self.click.get_raw()
        raw_array = raw_array[len(raw_array)//2:]
        self.click = pygame.mixer.Sound(buffer=raw_array)        
        self.screen = pygame.display.set_mode(self.size)

        self.audio = True
        self.clock = pygame.time.Clock()
        self.graphics = True
        
        self.level = json.load(open('data/stats.json', 'r')).get('level')
        self.tile_group = 0

        self.tile_variant = 0
        self.bg = pygame.transform.scale(pygame.image.load("data/images/bg/bg.png"), self.screen.get_size())
        self.font = pygame.font.SysFont("Arial" , 45 , bold = False, italic = True)
        self.audio = True
        self.offset = [0,0]
        self.page = 0



    def Main(self):
        while True:
            self.screen.blit(self.bg, (0,0))
            text = self.font.render('Start', True, (0,255,0))
            pos = [self.screen.get_width()/2-text.get_width()/2, self.screen.get_height()/2-text.get_height()/2-20]
            self.screen.blit(text, pos)
            settings = self.font.render('settings', True, (0,255,0))
            settings_pos = [self.screen.get_width()/2-settings.get_width()/2, self.screen.get_height()/2-settings.get_height()/2+60]
            self.screen.blit(settings, settings_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if pygame.Rect(*pos, *text.get_size()).collidepoint(*pygame.mouse.get_pos()):
                            if self.audio:
                                self.click.play()
                            self.start()
                        if pygame.Rect(*settings_pos, *settings.get_size()).collidepoint(*pygame.mouse.get_pos()):
                            if self.audio:
                                self.click.play()
                            self.settings()

            pygame.display.update()


    def settings(self):
        while True:
            self.screen.blit(self.bg, (0,0))
            text = self.font.render('ON' if self.audio else "OFF", True, (0,255,0))
            pos = [self.screen.get_width()/2-text.get_width()/2+110, self.screen.get_height()/2-text.get_height()/2]
            self.screen.blit(text, pos)
            text = self.font.render('audio :', True, (0,255,0))
            pos = [self.screen.get_width()/2-text.get_width()/2, self.screen.get_height()/2-text.get_height()/2]
            self.screen.blit(text, pos)
            returntext = self.font.render('back', True, (0,255,0))
            returnpos = [self.screen.get_width()/2-text.get_width()/2+0, self.screen.get_height()/2-text.get_height()/2+60]
            self.screen.blit(returntext, returnpos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game = Game()
                        game.run()                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 :
                        if pygame.Rect(*pos, *text.get_size()).collidepoint(*pygame.mouse.get_pos()):
                            self.audio = not self.audio
                            if self.audio:self.click.play()
                        if pygame.Rect(*returnpos, *returntext.get_size()).collidepoint(*pygame.mouse.get_pos()):
                            if self.audio:self.click.play()
                            return
                        
                        
            pygame.display.update()

    def start(self):
        data = json.load(open('data/stats.json', 'r'))
        level = data.get('level', 0)
        while True:
            self.screen.blit(self.bg, (0,0))        
            text = self.font.render('new game', True, (0,255,0))
            pos = [self.screen.get_width()/2-text.get_width()/2 - (0 if not level else 130), self.screen.get_height()/2-text.get_height()/2-30]
            self.screen.blit(text, pos)
            settings = self.font.render('load save', True, (0,255,0))
            load_pos = [self.screen.get_width()/2-settings.get_width()/2 + (1300 if not level else 130), self.screen.get_height()/2-settings.get_height()/2-30]
            self.screen.blit(settings, load_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if pygame.Rect(*pos, *text.get_size()).collidepoint(*pygame.mouse.get_pos()):
                            write_stats('data/stats.json', {'level':0, 'deaths': 0})    
                            if self.audio:self.click.play()
                            Game(audio=self.audio).run()
                        if pygame.Rect(*load_pos, *settings.get_size()).collidepoint(*pygame.mouse.get_pos()):
                            if self.audio:self.click.play()
                            Game(audio=self.audio).run()

            pygame.display.update()


if __name__ == "__main__":
    Menu().Main()
