import pygame
from scripts.particles import Particle
from scripts.sparks import Spark
import time
import random
import math

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.action =  ''
        self.anim_offset = (-3,-3)
        self.flip = False
        self.last_mov = [0,0]
        self.set_action('idle')
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '_' +self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0] ,movement[1] + self.velocity[1])

        self.last_mov = movement
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True 

           
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()
        
    def render(self, surf, offset = (0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1]+ self.anim_offset[1]))
        

class Enemy(PhysicsEntity):
    def __init__(self, game,  pos, size):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0]-5, self.size[1])


    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx +(-7 if self.flip else +7), self.pos[1] + tilemap.tile_size)):
                if (self.collisions['right'] == True or self.collisions['left'] == True):
                    self.flip = not self.flip
                movement = (movement[0] - 1.5 if self.flip else 1.5, movement[1])
            else:
                
                self.flip = not self.flip
            self.walking = max(self.walking -1, 0)
        elif random.random() < 0.01:
            self.walking = random.randint(30,120)
        self.set_action('idle')
        super().update(tilemap, movement)

        if abs(self.game.player.dashing) <= 50:
            if self.game.player.rect().colliderect(self.rect()):
                if self.game.audio:
                    self.game.sfx['hit'].play()
                self.game.dead += 1


        if abs(self.game.player.dashing) >= 50:
            if self.game.player.rect().colliderect(self.rect()):
                if self.game.audio:
                    self.game.sfx['hit'].play()
                return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.dashing = 0
        self.last_shot = time.time()
        self.anim_offset = (-13,-26)

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0]-10, self.size[1]-10)
        

    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=[movement[0]*2, movement[1]])
        self.air_time += 1
        
        if self.air_time > 120:
            if not self.game.dead:
                if self.game.audio:
                    self.game.sfx['hit'].play()
                self.game.screenshake = max(16,self.game.screenshake)
            self.game.dead = 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)

        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        if abs(self.dashing) in {60,50}:
            for i in range(20):
                    angle = random.random() * math.pi *2
                    speed = random.random() * 0.5 +0.5
                    pvelecoty = [math.cos(angle)*speed, math.sin(angle)*speed]
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelecoty, frame= random.randint(0,7)))

        if self.dashing > 0:
            self.dashing = max(self.dashing - 1, 0)
        else:
            self.dashing = min(self.dashing + 1, 0)


        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) /self.dashing *8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelecoty = [abs(self.dashing) / self.dashing * random.random() *3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelecoty, frame= random.randint(0,7)))


    def render(self, surf, offset=(0,0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset)

    def jump(self):
        if self.jumps and self.air_time <= 5:
            self.jumps =0
            self.velocity[1] = -4
            self.air_time = 5
            return True

    def dash(self):
        if not self.dashing:
            if self.game.audio:
                self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60                
    def shoot(self):
        if time.time() - self.last_shot > 0.2:
            self.last_shot = time.time()
            if self.game.audio:
                self.game.sfx['shoot'].play()
            if self.flip:
                self.game.bullets.append([[self.rect().centerx -7, self.rect().centery],-2.5, 0])
                for i in range(4):
                    self.game.sparks.append(Spark(self.game.bullets[-1][0], random.random() - 0.5 + math.pi, 2+ random.random()))
            else:
                self.game.bullets.append([[self.rect().centerx +7, self.rect().centery],2.5, 0])                       
                for i in range(4):
                    self.game.sparks.append(Spark(self.game.bullets[-1][0], random.random() - 0.5, 2+ random.random())) 
            self.set_action('shoot')
