import pygame
from settings import vertical_tile_number, tile_size, screen_width


class ParallaxBackground:
    def __init__(self, speed, image_paths):
        self.speed = speed
        self.bg_images = []
        for path in image_paths:
            bg_image = pygame.image.load(path).convert_alpha()
            bg_image = pygame.transform.scale(bg_image, (1200,720))
            self.bg_images.append(bg_image)
        self.bg_width = self.bg_images[0].get_width()

    def draw(self, surface):
        num_images = len(self.bg_images)
        offset = 0
        for i in range(num_images):
            surface.blit(self.bg_images[i], (offset, 0))
            surface.blit(self.bg_images[i], (offset - self.bg_width, 0))
            offset += self.speed * (i + 0.5)

