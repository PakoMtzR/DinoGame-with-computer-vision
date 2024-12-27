# Clase para los objetos dentro del juego
class Object:
    def __init__(self, x, y, image):
        self.image = image
        self.x = x
        self.y = y
    
    # Verifica si el objeto se sigue mostando en pantalla
    def on_screen(self):
        return self.x + self.image.get_width() >= 0
    
    # Mueve el objeto en el eje x a una cierta velocidad
    def move(self, screen, velocity):
        self.x -= velocity
        if not self.on_screen():
            self.x = screen.get_width()
    
    # Dibuja el objeto
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))