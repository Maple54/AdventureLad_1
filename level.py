import pygame 
from support import import_csv_layout, import_cut_graphics,import_folder
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile,Stones,Coin
from enemy import Enemy
from player import Player
from particles import ParticleEffect
from background import ParallaxBackground


 

class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # audio 
        self.coin_sound = pygame.mixer.Sound('audio/effects/coin.wav')
        

        #player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

    	# dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        #terrain
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        #grass setup 
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout,'grass')

        #crates
        stones_layout = import_csv_layout(level_data['stones'])
        self.stones_sprites = self.create_tile_group(stones_layout,'stones')

        #coins
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout,'coins')

        #enemy 
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')

        #constraints
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout,'constraints')

        self.sky = ParallaxBackground(speed=2, image_paths=[
        "graphics/terrain/background/plx-1.png",
        "graphics/terrain/background/plx-2.png",
        "graphics/terrain/background/plx-3.png",
        "graphics/terrain/background/plx-4.png",
    ])


    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()
        tile_list = None
        if type == 'terrain':
            tile_list = import_cut_graphics('C:/Visual studio code/repos/Main Game/levels/tilesets/tileset.png')
        elif type == 'grass':
            tile_list = import_cut_graphics('C:/Visual studio code/repos/Main Game/levels/tilesets/grass.png')

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    if type == 'terrain' or type == 'grass':
                        if int(val) < len(tile_list):
                            tile_surface = tile_list[int(val)]
                            sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == 'stones':
                        sprite = Stones(tile_size, x, y)
                    elif type == 'coins':
                        sprite = Coin(tile_size, x, y, 'graphics/coins')
                    elif type == 'enemies':
                        sprite = Enemy(tile_size, x, y)
                    elif type == 'constraints':
                        sprite = Tile(64, x, y)
                    sprite_group.add(sprite)

        return sprite_group
    
    def player_setup(self,layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x,y),self.display_surface,self.create_jump_particles)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('graphics/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,hat_surface)
                    self.goal.add(sprite)
                   
    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
                enemy.reverse()
    
    def create_jump_particles(self,pos):
            if self.player.sprite.facing_right:
                pos -= pygame.math.Vector2(10,5)
            else:
                pos += pygame.math.Vector2(10,-5)
            jump_particle_sprite = ParticleEffect(pos,'jump')
            self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
            player = self.player.sprite
            player.collision_rect.x += player.direction.x * player.speed
            collidable_sprites = self.terrain_sprites.sprites() + self.stones_sprites.sprites() 
            for sprite in collidable_sprites:
                if sprite.rect.colliderect(player.collision_rect):
                    if player.direction.x < 0: 
                        player.collision_rect.left = sprite.rect.right
                        player.on_left = True
                        self.current_x = player.rect.left
                    elif player.direction.x > 0:
                        player.collision_rect.right = sprite.rect.left
                        player.on_right = True
                        self.current_x = player.rect.right

    def vertical_movement_collision(self):
            player = self.player.sprite
            player.apply_gravity()
            collidable_sprites = self.terrain_sprites.sprites() + self.stones_sprites.sprites() 

            for sprite in collidable_sprites:
                if sprite.rect.colliderect(player.collision_rect):
                    if player.direction.y > 0: 
                        player.collision_rect.bottom = sprite.rect.top
                        player.direction.y = 0
                        player.on_ground = True
                    elif player.direction.y < 0:
                        player.collision_rect.top = sprite.rect.bottom
                        player.direction.y = 0
                        player.on_ceiling = True

            if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
                player.on_ground = False

    def scroll_x(self):
            player = self.player.sprite
            player_x = player.rect.centerx
            direction_x = player.direction.x

            if player_x < screen_width / 4 and direction_x < 0:
                self.world_shift = 8
                player.speed = 0
            elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
                self.world_shift = -8
                player.speed = 0
            else:
                self.world_shift = 0
                player.speed = 6

    def get_player_on_ground(self):
            if self.player.sprite.on_ground:
                self.player_on_ground = True
            else:
                self.player_on_ground = False
    
    def create_landing_dust(self):
            if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
                if self.player.sprite.facing_right:
                    offset = pygame.math.Vector2(10,15)
                else:
                    offset = pygame.math.Vector2(-10,15)
                fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
                self.dust_sprite.add(fall_dust_particle)

    def check_coin_collisions(self):
            collided_coins = pygame.sprite.spritecollide(self.player.sprite,self.coin_sprites,True)
            if collided_coins:
                self.coin_sound.play()
                # for coin in collided_coins:
                #     self.change_coins(coin.value)
    
    def run(self): 
            #background
        self.sky.draw(self.display_surface)

        # dust particles 
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        #terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        
        
        #enemy
        self.enemy_sprites.update(self.world_shift)      
        self.constraint_sprites.update(self.world_shift)     
        self.enemy_collision_reverse()    
        self.enemy_sprites.draw(self.display_surface)

         #stones
        self.stones_sprites.update(self.world_shift)  
        self.stones_sprites.draw(self.display_surface)

        #grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)
        
        
        #coins  
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

    
            # player sprites
        self.player.update()
        self.horizontal_movement_collision()
                
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
                
        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_coin_collisions()
            
            


            
    
            
        

