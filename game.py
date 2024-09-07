import math
import random
import sys
import pygame
import time
import os
from scripts.utils import load_image, load_images, Animation, write_stats, load_stats, scale_images, load_sheet, center_text
from scripts.entities import PhysicsEntity , Player, Enemy
from scripts.tilemap import Tilemap
from scripts.sparks import Spark
from scripts.particles import Particle
from scripts.paralex import Paralex
class Game:
    def __init__(self, size = (640, 480), audio=True):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode(size)
        self.display = pygame.Surface((size[0]/2, size[1]/2))
        self.display2 = pygame.Surface((size[0]/2, size[1]/2))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(os.path.join('data', 'font.TTF'), 23)
        self.movement = [False, False]
        self.custom = False
        self.tile_size = 32
        self.max_level = len(os.listdir(os.path.join('data', 'maps'))) - 1
        self.assets = {
            'bg' : Paralex(scale_images(load_images('bg'), self.display.get_size())[:-1], [[3**i, i*300] for i in range(1, len(load_images('bg')))]),
            'tiles': scale_images(load_images('tiles/'), (self.tile_size, self.tile_size)),
            'gun': load_image('player.png'),
            'spawners': load_image('entities/enemy/Enemy.png'),
            'bullet': load_sheet('player.png', 4, (32 ,32), 1, 4),
            'player': load_image('entities/player.png'),
            'player_idle': Animation(scale_images([load_sheet('player.png', 1, (32 ,32),1)], (48,48)), 6),
            'player_run': Animation(  scale_images(load_sheet('player.png', 3, (32 ,32),4),  (48,48)), 12),
            'player_jump': Animation( scale_images(load_sheet('player.png', 3, (32 ,32),4),  (48,48)), 31),
            'player_shoot': Animation(load_sheet('player.png', 4, (32 ,32),4), 6),
            'enemy_idle': Animation(scale_images([load_image('entities/enemy/Enemy.png')], (32 ,32))),
            'particle': Animation(load_images('particles/particle'), dur = 6, loop=False),
        }
    
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2 )
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        self.stats = load_stats('data/stats.json')
        self.start_time = self.stats.get('start_time', time.time())
        self.player = Player(self, (50, 50), (32, 32))
        

        self.tilemap = Tilemap(self, tile_size=32)
        self.screenshake = 0
        self.dead = 0
        self.mode = 0
        self.audio = audio
        self.load_map(self.stats['level'])


    def load_map(self, id = ""):
        self.tilemap.load(os.path.join('data', 'maps', f'{id}.json'))
        self.dead = 0
        
        self.leaf_spawners = []
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners',0),('spawners',1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (32,32)))
        self.player.air_time = 0
        self.level_started = time.time()
        self.transition = - 30
        self.sparks = []
        self.particles = []
        self.bullets = []
        self.scroll = [0,0]


    def run(self):
        if self.audio:
            self.sfx['ambience'].play(-1)
        while True:

            self.display.fill((0,0,0))
            if not self.enemies and self.stats['level'] != 'won':
                    self.transition += 1
                    if self.transition > 30:  
                        if  self.stats['level'] +1 <= self.max_level:
                            self.stats['level'] += 1
                        else:
                            self.stats['level'] = 'won'
                            write_stats('data/stats.json', {'level':0, 'deaths': 0})    
                        write_stats('data/stats.json', self.stats)
                        try:
                            self.load_map(self.stats['level'])
                        except FileNotFoundError:
                            pass
            
            

            if self.transition <0:
                self.transition +=1

            if self.dead:
                self.dead +=1
                self.stats['deaths'] += 1
                if self.dead >= 10:
                    self.transition = min(self.transition + 1, 30)
                if self.custom:
                    if self.dead > 40:
                        try:
                            self.load_map()
                        except FileNotFoundError:
                            pass
                if not self.custom:
                    if self.dead > 40:
                        try:
                            self.load_map(self.stats['level'])
                        except FileNotFoundError:
                            pass
            
            

            self.screenshake = max(self.screenshake - 1,0)
            lag = 0.5

            if (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])/30 > lag or (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])/10 < -lag:
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])/30
            if (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1])/30 > lag or (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1])/10 < -lag:
                self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1])/30
            self.rscroll = (int(self.scroll[0]), int(self.scroll[1]))


            self.assets['bg'].draw(self.display, self.rscroll)
            
            self.tilemap.render(self.display, offset = self.rscroll)  
            
            for rect in self.leaf_spawners:
                if random.random() *79999 < rect.width * rect.height:
                    pos =(rect.x + random.random() *rect.width, rect.y + random.random() *rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0,18)))



            for enemy in self.enemies:
                kill = enemy.update(self.tilemap)
                enemy.render(self.display, offset=self.rscroll)
                if kill:
                    self.screenshake = max(self.screenshake ,16)
                    self.enemies.remove(enemy)
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display,offset = self.rscroll)
                
            for bullet in self.bullets.copy():
                bullet[0][0] += bullet[1]
                bullet[2] += 1
                img = self.assets['bullet']
                self.display.blit(img,(bullet[0][0] - img.get_width()/2 - self.rscroll[0], bullet[0][1] - img.get_height()/2 - self.rscroll[1]))
                if self.tilemap.solid_check(bullet[0]):
                    self.bullets.remove(bullet)
                    for i in range(4):
                            self.sparks.append(Spark(bullet[0], random.random() - 0.5 + (math.pi if bullet[1] > 0 else 0), 2+ random.random()))
                elif bullet[2] > 60*7:
                    self.bullets.remove(bullet)
                for enemy in self.enemies:
                    if enemy.rect().collidepoint(bullet[0]):
                        try:
                            self.enemies.remove(enemy)
                            self.bullets.remove(bullet)
                        except Exception as e:
                            print(e)
                        if self.audio:
                            self.sfx['hit'].play()
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(enemy.rect().center,angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', enemy.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5,] ,frame=random.randint(0,7)))
                        

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=self.rscroll)
                if kill:
                    self.sparks.remove(spark)


            if self.mode ==1:
                mask = pygame.mask.from_surface(self.display)
                display_sillhoutte = mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
                for offset in [(-1,0),(1,0),(0,-1),(0,1)]:
                    self.display2.blit(display_sillhoutte,offset)
            for particle in self.particles:
                kill = particle.update()
                particle.render(self.display, offset=self.rscroll)
                if particle.p_type == 'leaf':
                    particle.pos[0] += math.sin(100000000) * 0.3
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.player.jump():
                            if self.audio:
                                self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                        

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False


            if self.transition:
                s = pygame.Surface(self.display.get_size())
                pygame.draw.circle(s,(255,255,255), (self.display.get_width()//2,self.display.get_height()//2),(200-abs(self.transition) * 8))
                s.set_colorkey((255,255,255))
                self.display.blit(s,(0,0))

            self.display2.blit(self.display,(0,0))

            shakeset = (random.random() * self.screenshake - self.screenshake/2, random.random() * self.screenshake - self.screenshake/2)
            self.screen.blit(pygame.transform.scale(self.display2, self.screen.get_size()), shakeset)
            self.render_text()
            pygame.display.update()
            self.clock.tick(60)


    def render_text(self):
        if self.stats.get('level') == 0 and time.time() - self.level_started <= 30:
            text = 'use the arrow keys to move and space bar to shoot'.replace(' ', '   ') 
            text = self.font.render(text , True, (0,255,0))
            self.screen.blit(text, (center_text(text, self.screen)[0], 30))
        elif self.stats.get('level') == 1:

            text = 'press the x key to dash'.replace(' ', '   ') if time.time() - self.level_started <= 10 else 'when dashing you become invincible'.replace(' ', '   ')
            text = self.font.render(text , True, (0,255,0))
            self.screen.blit(text, (center_text(text, self.screen)[0], 30))
        elif self.stats.get('level') == 'won':
            self.time_taken = time.strftime('%H:%M:%S', time.gmtime(self.level_started-self.start_time))
            font = pygame.font.Font(os.path.join('data', 'font.TTF'), 20)
            text = f'''Congratulation you have beaten the game with only {self.stats.get("deaths")} deaths'''.replace(' ', '   ') 
            text = font.render(text , True, (0,255,0))
            self.screen.blit(text, (center_text(text, self.screen)[0], 30))
        if str(self.stats.get('level')).isdigit():
            text = f"Level {int(self.stats.get('level'))+1}"
            text = self.font.render(text , True, (0,255,0))
            self.screen.blit(text, (0, 0))