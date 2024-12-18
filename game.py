import pygame   # Libreria para el desarrollo de videojuegos
import os       # Libreria para manejo de archivos
import random

# Inicializamos pygame
pygame.init()
FPS = 60
clock = pygame.time.Clock()

# Cargamos logotipo del juego
dino_img = pygame.image.load(os.path.join("my-assets\dino", "dino_0.png"))

# Configuracion de la pantalla
WIDTH, HEIGTH = 750, 400
GROUND_LEVEL = HEIGTH*3//4
screen = pygame.display.set_mode((WIDTH, HEIGTH))   # Definimos ancho y alto de la pantalla
pygame.display.set_caption("Dino Game")             # Configuramos titulo de la barra
pygame.display.set_icon(dino_img)                   # Cargamos el icono de la app

# Colores
BLACK = (25,25,25)
WHITE = (220,220,220)
GRAY = (100,100,100)

# Fuente
font = pygame.font.Font(None, 28)

class Dino:
    def __init__(self):
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
        self.collision_image = pygame.image.load(os.path.join("my-assets\dino", "dino_3.png"))

        self.current_frame = 0
        self.animation_time = 0

        self.image = self.jump_image
        self.ground_level = GROUND_LEVEL - self.image.get_height() + 10
        
    def jump(self):
        if not self.jumping:
            self.velocity = -10
            self.jumping = True
    
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

    def draw(self, collision):
        if collision:
            self.image = self.collision_image
        elif not self.jumping:
            self.image = self.running_images[self.current_frame]
        else:
            self.image = self.jump_image

        screen.blit(self.image, (self.x, self.y))

class Object:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
    
    def on_screen(self):
        return self.x + self.image.get_width() >= 0
    
    def move(self, velocity):
        self.x -= velocity
        if not self.on_screen():
            self.x = WIDTH
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))
    
class Cactus(Object):
    # GROUND_LEVEL - self.image.get_height() + 10,
    def __init__(self):
        super().__init__(
            WIDTH,
            GROUND_LEVEL - 46 + 10,
            pygame.image.load(os.path.join("my-assets\cactus", "cactus.png"))
        )

class Cloud(Object):
    def __init__(self):
        super().__init__(
            random.randint(0, WIDTH), 
            random.randint(0, int(HEIGTH*0.4)),
            pygame.image.load(os.path.join("my-assets\clouds", "cloud.png"))
        )
    
class Game:
    def __init__(self):
        self.player = Dino()
        self.velocity = 4
        self.cactus = Cactus()
        self.score = 0
        self.collision = False
        self.running_game = True
        self.count = 1
        self.clouds = [Cloud() for i in range(6)]
 
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running_game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.collision:
                        self.restart()
                    else:
                        self.player.jump()
    
    def update(self):
        if self.collision:
            return

        for cloud in self.clouds:
            cloud.move(self.velocity)

        # Actualizazr dinosaurio
        self.player.move()
        self.player.animate()

        # Actualizar cactus
        self.cactus.move(self.velocity)
        
        # Detectar colisiones
        if (self.player.x < self.cactus.x + self.cactus.image.get_width()) and (self.player.x + self.player.image.get_width() > self.cactus.x) and (self.player.y < self.cactus.y + self.cactus.image.get_height()) and (self.player.y + self.player.image.get_height() > self.cactus.y):
            self.collision = True

        # Incrementar puntuacion
        self.score += 1
        if self.score == self.count*2*FPS:
            self.count += 1
            self.velocity += 1

    def draw(self):
        # Dibujar escenario
        screen.fill(WHITE)
        pygame.draw.line(screen, GRAY, (0,300), (WIDTH, 300), width=1)
        for cloud in self.clouds:
            cloud.draw()

        # Dibujar dinosaurio
        self.player.draw(self.collision)

        # Dibujar cactus
        self.cactus.draw()

        # Escribir el "score"
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10,10))

        # Mostrar mensaje de reinicio
        if self.collision:
            message = font.render("Press SPACE to restart", True, BLACK)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGTH // 2))
        pygame.display.update()
    
    def restart(self):
        self.player = Dino()
        self.cactus = Cactus()
        self.velocity = 4
        self.score = 0
        self.collision = False
        self.count = 1
    
    def run(self): 
        while self.running_game:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# Ejecutar el juego
game = Game()
game.run()
pygame.quit()