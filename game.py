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
pygame.display.set_caption("Dino-Game")             # Configuramos titulo de la barra
pygame.display.set_icon(dino_img)                   # Cargamos el icono de la app

# Colores
BLACK = (25,25,25)
WHITE = (220,220,220)
GRAY = (100,100,100)
GRAY_DARKED = (80,80,80)

# Fuentes
font_24 = pygame.font.Font(None, 24)
font_20 = pygame.font.Font(None, 20)

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

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, collision):
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

# Clase para los objetos dentro del juego
class Object:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
    
    # Verifica si el objeto se sigue mostando en pantalla
    def on_screen(self):
        return self.x + self.image.get_width() >= 0
    
    # Mueve el objeto en el eje x a una cierta velocidad
    def move(self, velocity):
        self.x -= velocity
        if not self.on_screen():
            self.x = WIDTH
    
    # Dibuja el objeto
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

        # Crear mascara de colisiones
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, velocity):
        self.x -= velocity
        if not self.on_screen():
            del self

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

class Cloud(Object):
    def __init__(self):
        super().__init__(
            random.randint(0, WIDTH), 
            random.randint(0, int(HEIGTH*0.4)),
            pygame.image.load(os.path.join("my-assets\clouds", "cloud.png"))
        )
    
class Game:
    def __init__(self):
        # Banderas de control de juego
        self.running_game = True            # Para saber si el juego debe seguir ejecutandore
        self.blink_control_enable = False   # Para (des/ha)bilitar el control por parpadeo
        self.collision = False              # Para saber si el jugador ha perdido la partida
        self.new_record_flag = False        # Para conocer si el jugador a obtenido un nuevo record
        
        # Elementos del juego
        self.player = Dino()    # Creamos el dinosaurio wooasss
        self.cactuses = []      # Lista para guardar los cactus
        self.velocity = 4       # Variable que modifica la dificultad del juego

        # Variables para las metricas del jugador
        self.score = 0
        self.high_score = self.load_high_score()
        
        # Variable relacionada con el tiempo del juego
        self.count = 1

        # Creamos las nubes del escenario
        self.clouds = [Cloud() for _ in range(5)]

        # Sonidos del juego
        self.new_level_sound = pygame.mixer.Sound(os.path.join("my-assets\sounds", "point-sound.mp3"))
        self.collision_sound = pygame.mixer.Sound(os.path.join("my-assets\sounds", "lose_funny_retro_video-game.mp3"))

        # Creamos los textos que no requieren ser animados(actualizados) durante el juego para mejorar el rendimiento
        self.restart_message = font_24.render("Press SPACE to restart", True, BLACK)
        self.jump_control_text = font_20.render("[SPACE] - Jump", True, GRAY_DARKED)
        self.close_game_control_text = font_20.render("[ESC] - Close the game", True, GRAY_DARKED)
        font_20.set_strikethrough(True)
        self.blink_disable_text = font_20.render("[Q] - Blink control", True, GRAY_DARKED)
        font_20.set_strikethrough(False)
        self.blink_enable_text = font_20.render("[Q] - Blink control", True, GRAY_DARKED)

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
                
                # Tecla para des/habilitar el control por parpadeo
                if event.key == pygame.K_q:
                    self.blink_control_enable = not self.blink_control_enable
                
                # Tecla para salir del juego
                if event.key == pygame.K_ESCAPE:
                    self.running_game = False
        
        # Control de saltos detectando el parpadeo usando mediapipe
        if self.blink_control_enable and detect_blink():
            if self.collision:
                self.restart()
            else:
                self.player.jump()

    # Actualiza el estado de los elementos del juego
    def update(self):
        # Si existe una colision no debe actualizarse nada porque el juego ha acabado
        if self.collision:
            return

        # Movemos todas las nubes
        for cloud in self.clouds:
            cloud.move(self.velocity)

        # Actualizazr dinosaurio
        self.player.move()
        self.player.animate()

        # Actualizar cactus
        if random.randrange(0, 2*FPS) == 1:
            self.cactuses.append(Cactus())
        
        for cactus in self.cactuses:
            cactus.move(self.velocity)
        
        # Incrementar puntuacion
        self.score += 1
        self.count += 1

        # Cada n segundos aumenta la dificultad del juego
        if self.count == 4*FPS:
            self.new_level_sound.play()
            self.velocity += 1
            self.count = 0

        # Condicion para terminar la partida
        # Detectar si existen colisiones entre el dinosaurio y los cactus
        for cactus in self.cactuses:
            offset = (cactus.x - self.player.x, cactus.y - self.player.y)
            if self.player.mask.overlap(cactus.mask, offset):
                self.collision = True
                self.collision_sound.play()

                # Verificamos si el jugador alcanzo un nuevo record
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.new_record_flag = True
                    self.save_high_score()          

    # Dibuja todos los elementos visibles del juego
    def draw(self):
        # Dibujar escenario
        screen.fill(WHITE)
        pygame.draw.line(screen, GRAY, (0,300), (WIDTH, 300), width=1)
        for cloud in self.clouds:
            cloud.draw()

        # Dibujar dinosaurio
        self.player.draw(self.collision)

        # Dibujar los cactus
        for cactus in self.cactuses:
            cactus.draw()

        # Escribir indicadores ("score" y "high_score")
        high_score_text = font_24.render(f"Best: {self.high_score}", True, GRAY_DARKED)
        screen.blit(high_score_text, (10,10))
        
        score_text = font_24.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, high_score_text.get_height() + 10))

        # Escribimos mensaje de reinicio si existe una colision
        if self.collision:
            screen.blit(self.restart_message, (WIDTH // 2 - self.restart_message.get_width() // 2, HEIGTH // 2))

            # Escribimos un mensaje si rompio el record
            if self.new_record_flag:
                new_record_text = font_24.render(f"New record: {self.high_score}!", True, GRAY_DARKED)
                screen.blit(new_record_text, (WIDTH // 2 - new_record_text.get_width() // 2, HEIGTH // 2 - new_record_text.get_height() - 5))

        # Escribimos guia de controles
        screen.blit(self.close_game_control_text, (10, HEIGTH - self.close_game_control_text.get_height() - 5))
        screen.blit(self.jump_control_text, (10, HEIGTH - self.close_game_control_text.get_height() - self.jump_control_text.get_height() - 5))
        
        if not self.blink_control_enable:
            screen.blit(self.blink_disable_text, (10, HEIGTH - self.close_game_control_text.get_height() - self.jump_control_text.get_height() - self.blink_disable_text.get_height() - 5))
        else:
            screen.blit(self.blink_enable_text, (10, HEIGTH - self.close_game_control_text.get_height() - self.jump_control_text.get_height() - self.blink_enable_text.get_height() - 5))

        # Actualiza la pantalla
        pygame.display.update()
    
    # Funcion para reiniciar el juego
    def restart(self):
        # Limpiamos las banderas de control del juego
        self.new_record_flag = False   
        self.collision = False
        
        self.player = Dino()    # Recreamos el dinosauuurio
        self.cactuses = []      # Eliminamos todos los cactus
        self.velocity = 4       
        self.score = 0          # Resetamos el score
        self.count = 0
    
    # Carga el record mas alto almacenado en "high_score.txt"
    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    # Guarda el "high score"
    def save_high_score(self):
        with open("high_score.txt", "w") as file:
            file.write(str(self.high_score))

    # Ejecuta el juego
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