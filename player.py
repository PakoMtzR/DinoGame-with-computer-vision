import pygame   # Libreria para el desarrollo de videojuegos
import os       # Libreria para manejo de archivos

# Clase dinosaurio (jugador)
class Dino:
    def __init__(self, screen):
        self.x = 70
        self.y = 50
        self.velocity = 0
        self.gravity = 0.5
        self.jumping = True

        # Cargar imagenes
        self.jump_image = pygame.image.load(os.path.join("my-assets\dino", "dino_0.png"))
        self.running_images = [
            pygame.image.load(os.path.join("my-assets\dino", "dino_1.png")),
            pygame.image.load(os.path.join("my-assets\dino", "dino_2.png"))
        ]
        self.collision_image = pygame.image.load(os.path.join("my-assets\dino", "dino_7.png"))

        # Cargar sonido de salto del dinosaurio
        self.jump_sound = pygame.mixer.Sound(os.path.join("my-assets\sounds", "jump-sound.mp3"))

        self.current_frame = 0
        self.animation_time = 0

        # Cargamos la imagen actual del
        self.image = self.jump_image

        # Crear mascara de colisiones
        self.mask = pygame.mask.from_surface(self.image)

        # Dato para limitar la caida del dinosaurio
        self.ground_level = (screen.get_height()*3//4) - self.image.get_height() + 10
        
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.velocity = -10
            self.jump_sound.play()
    
    def move(self):
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y >= self.ground_level:
            self.y = self.ground_level
            self.jumping = False
    
    def animate(self):
        if not self.jumping:
            self.animation_time += 1
            if self.animation_time % 10 == 0:
                self.current_frame = (self.current_frame + 1) % len(self.running_images)

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen, collision):
        # Cambiamos imagen dependiendo el estado del jugador
        if collision:
            self.image = self.collision_image
        elif not self.jumping:
            self.image = self.running_images[self.current_frame]
        else:
            self.image = self.jump_image

        # Actualizar la mascara del dinosaurio
        self.update_mask()

        # Dibujamos el dinosaurio en la panatalla
        screen.blit(self.image, (self.x, self.y))