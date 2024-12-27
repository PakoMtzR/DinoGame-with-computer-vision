import pygame
import random
import os
from object import Object

class Cloud(Object):
    def __init__(self, screen):
        super().__init__(
            random.randint(0, screen.get_width()), 
            random.randint(0, int(screen.get_height()*0.4)),
            pygame.image.load(os.path.join("my-assets\clouds", "cloud.png"))
        )