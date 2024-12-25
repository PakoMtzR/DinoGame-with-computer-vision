# Juego del Dinosaurio de Google
![Python](https://img.shields.io/badge/Python-3.x-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.9.x-green) ![Pygame](https://img.shields.io/badge/Pygame-2.x-yellow)

## Descripcion 
Este proyecto intenta ser un clon del famoso juego del dinosaurio de google usando pygame, puedes hacer los saltos con la barra espaciadora o bien puedes habilitar la deteccion de parpadeo para que el dinosaurio salte cuando parpades, esta funcionalidad fue hecha con mediapipe.

![DinoGame_img](/my-assets/captures/dino-game.png)

## Tecnologías utilizadas
- **Pygame**
- **OpenCV**
- **Mediapipe**

## Instalación
1. Clona el repositorio:
    ```bash
    git clone https://github.com/PakoMtzR/DinoGame-with-computer-vision.git
    ```
2. Crea un entorno virtual (opcional):
   ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/MacOS
    venv\Scripts\activate      # Windows
    ```
3. Instala las dependencias necesaria:
   ```bash
    pip install -r requirements.txt
    ```
4. Ejecuta el juego:
   ```bash
    python game.py
    ```