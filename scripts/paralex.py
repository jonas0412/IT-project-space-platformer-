import pygame
import time
import math
import random


class Paralex:
    def __init__(self, images, depths) -> None:
        self.images:list[pygame.Surface] = list(reversed(images))
        self.depths = list(reversed(depths))
        print(len(images) ,len(self.depths))

    
    def draw(self, screen, offset=(0,0)):
        for i, image in enumerate(self.images):
            for j in range(math.ceil(screen.get_width()/image.get_width())+1):
                screen.blit(image, ((-offset[0]/self.depths[i][0])%image.get_width()- j*image.get_width(), 0))

