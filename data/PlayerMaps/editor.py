import sys

import pygame

from scripts.utils import load_images, load, save
from scripts.tilemap import Tilemap
Render_scale = 2.0
class Editor:
    def __init__(self,size=(640, 480)):
        pygame.init()

        self.size = list(size)
        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode(size)
        self.display = pygame.Surface((int(self.size[0]//2), int(self.size[1]//2)))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False, False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
        }

        self.tilemap = Tilemap(self, tile_size=16)

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        

        self.clicking = False
        self.right_clicking = False
        self.offset = [0,0]
        self.save = False
        self.load = False
        self.ongrid = True
        self.level = 1

    def run(self):
        while True:
            self.display.fill((0,0,0))


            self.current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            self.current_tile_image.set_alpha(100)
            self.offset[0] += (self.movement[1] - self.movement[0])*2
            self.offset[1] += (self.movement[3] - self.movement[2])*2
            roffset = (int(self.offset[0]), int(self.offset[1]))
            try:
                self.tilemap.render(self.display, roffset)                                      
            except IndexError:
                pass
            
            self.display.blit(self.current_tile_image,(50,50))
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0]/Render_scale, mpos[1]/Render_scale)
            tile_pos = (int((mpos[0]+roffset[0])// self.tilemap.tile_size), int((mpos[1]+roffset[1])// self.tilemap.tile_size)) 
            if self.ongrid:
                self.display.blit(self.current_tile_image,(tile_pos[0]*self.tilemap.tile_size - roffset[0], tile_pos[1]*self.tilemap.tile_size - roffset[1]))
            else:
                self.display.blit(self.current_tile_image,(mpos[0] -8, mpos[1]-8))

            if self.clicking:
                if not self.ongrid:
                    self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + roffset[0] -8, mpos[1] + roffset[1] -8)})
                if self.ongrid:
                    self.tilemap.tilemap[str(tile_pos[0])+';'+str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile = str(tile_pos[0])+';'+str(tile_pos[1])
                if tile in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile]
                for tile in self.tilemap.offgrid_tiles.copy():
                        tile_img = self.assets[tile['type']][tile['variant']]
                        tile_r = pygame.Rect(tile['pos'][0] - roffset[0], tile['pos'][1] - roffset[1], tile_img.get_width(), tile_img.get_height())
                        if tile_r.collidepoint(mpos):
                            self.tilemap.offgrid_tiles.remove(tile)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True  
                    if event.button == 3:
                        self.right_clicking = True                          
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False     
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.tile_group = (self.tile_group -1) % len(self.tile_list)
                        self.tile_variant = 0
                    if event.key == pygame.K_2:
                        self.tile_variant = 0
                        self.tile_group = (self.tile_group +1) % len(self.tile_list)
                    if event.key == pygame.K_3:
                        self.tile_variant = (self.tile_variant -1) % len(self.assets[self.tile_list[self.tile_group]])
                    if event.key == pygame.K_4:
                        self.tile_variant = (self.tile_variant +1) % len(self.assets[self.tile_list[self.tile_group]])

                    if event.key == pygame.K_e:
                        try:
                            self.tilemap.export(save())
                        except FileNotFoundError:
                            pass
                    if event.key == pygame.K_r:
                        try:
                            self.tilemap.load(load())  
                        except FileNotFoundError:
                            pass
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid    
                    if event.key == pygame.K_t:
                        try:
                            self.tilemap.autotile()                                      
                        except IndexError:
                            pass
                    if event.key == pygame.K_p:

                        from menu import Menu
                        Menu().Main()     
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_e:
                        self.save = False 
                    if event.key == pygame.K_r:
                        self.reload = False                                            
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False           
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Editor().run()
