import json
import os
import pygame
from tkinter.filedialog import *
  
BASE_IMG_PATH = 'data/images/'

def load():
    return askopenfilename(initialdir=os.path.join('data', 'maps')) 
    

def save():
    return asksaveasfilename(initialdir=os.path.join('data', 'maps'))


def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def load_stats(path):
    return json.load(open(path, 'r'))

def write_stats(path, stats):
    json.dump(stats, fp=open(path, 'w'))


def load_sheet(path, row, size, count=0, start=0):
    image = pygame.image.load(os.path.join(BASE_IMG_PATH, path)).convert_alpha()
    images = []
    for i in range(start, start + (image.get_width()/size[0] if not count else count)):
        s = pygame.Surface(size)
        s.blit(image, (0,0), (size[0]*i, row*size[1], *size))
        s.set_colorkey((0,0,0))
        images.append(s)
    return images if len(images) > 1 else images[0]

def scale_images(images, size):
    for i, image in enumerate(images):
        if type(size) == list or type(size) == tuple:
            images[i] = pygame.transform.scale(image, size)
        elif type(size) == int or type(size) == float:
            images[i] = pygame.transform.scale_by(image, size)
    return images

def center_text(text, surf):
    return [surf.get_width() / 2 - text.get_width() / 2, surf.get_height() / 2, text.get_height() / 2]
    

class Animation:
    def __init__(self, image, dur=5, loop=True):
        self.image = image
        self.dur = dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.image, self.dur, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.dur * len(self.image))
        else:
            self.frame = min(self.frame + 1 ,self.dur * len(self.image) -1)
            if self.frame >= self.dur * len(self.image) -1:
                self.done = True
    
    def img(self):
        return self.image[int(self.frame/self.dur)]
        