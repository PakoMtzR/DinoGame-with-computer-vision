import pygame
import os
from object import Object

class Cactus(Object):
    # GROUND_LEVEL - self.image.get_height() + 10,
    def __init__(self, screen):
        super().__init__(
            screen.get_width(),
            (screen.get_height()*3//4) - 46 + 10,
            pygame.image.load(os.path.join("my-assets\cactus", "cactus.png"))
        )

        # Crear mascara de colisiones
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, velocity):
        self.x -= velocity
        if not self.on_screen():
            del self