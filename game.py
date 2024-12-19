import pygame   # Libreria para el desarrollo de videojuegos
import os       # Libreria para manejo de archivos
import random   # Libreria para el manejo de numeros aleatorios

import cv2              # Libreria para el manejo de imagenes
import mediapipe as mp  # Libreria para la deteccion del parpadeo

# Configuracion de mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Inicializamos la camara
cap = cv2.VideoCapture(0)  

# Función para detectar el parpadeo
def detect_blink():
    ret, frame = cap.read()
    if not ret:
        return False
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Puntos de referencia para los ojos
            left_eye = [face_landmarks.landmark[i] for i in [145, 159]]
            right_eye = [face_landmarks.landmark[i] for i in [374, 386]]

            # Calcular distancias
            left_eye_dist = abs(left_eye[0].y - left_eye[1].y)
            right_eye_dist = abs(right_eye[0].y - right_eye[1].y)

            # Detectar parpadeo si las distancias son pequeñas
            if left_eye_dist < 0.02 and right_eye_dist < 0.02:
                return True
    return False

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

# Clase dinosaurio (jugador)
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

        # Cargar sonido de salto del dinosaurio
        self.jump_sound = pygame.mixer.Sound(os.path.join("my-assets\sounds", "jump-sound.mp3"))

        self.current_frame = 0
        self.animation_time = 0

        self.image = self.jump_image
        self.ground_level = GROUND_LEVEL - self.image.get_height() + 10
        
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

    def draw(self, collision):
        # Cambiamos imagen dependiendo el estado del jugador
        if collision:
            self.image = self.collision_image
        elif not self.jumping:
            self.image = self.running_images[self.current_frame]
        else:
            self.image = self.jump_image

        # Dibujamos el dinosaurio en la panatalla
        screen.blit(self.image, (self.x, self.y))

# Clase para los objetos dentro del juego
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
        self.running_game = True
        self.blink_control_enable = False
        
        self.player = Dino()
        self.collision = False
        self.velocity = 4
        self.cactus = Cactus()
        self.score = 0
        self.count = 1

        # Creamos las nubes del escenario
        self.clouds = [Cloud() for i in range(6)]

        # Sonidos del juego
        self.new_level_sound = self.die_sound = pygame.mixer.Sound(os.path.join("my-assets\sounds", "point-sound.mp3"))
        self.collision_sound = pygame.mixer.Sound(os.path.join("my-assets\sounds", "pacman-dies.mp3"))

    # Funcion para manejar los eventos dentro del juego
    # cierre del juego, teclado, parpadeo, etc.
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
        
        # Control de saltos detectando el parpadeo usando mediapipe
        if self.blink_control_enable and detect_blink():
            if self.collision:
                self.restart()
            else:
                self.player.jump()

    # Actualiza el estado de los elementos del juego
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
            self.collision_sound.play()

        # Incrementar puntuacion
        self.score += 1
        if self.score == self.count*4*FPS:
            self.new_level_sound.play()
            self.count += 1
            self.velocity += 1

    # Dibuja todos los elementos visibles del juego
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

        # Actualiza la pantalla
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

# Libera los recursos cuando se cierre el juego
cap.release()
cv2.destroyAllWindows()
pygame.quit()