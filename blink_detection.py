import cv2              # Libreria para el manejo de imagenes
import mediapipe as mp  # Libreria para la deteccion del parpadeo
import time             # Libreria para el manejo del tiempo

class Blink_Detector:
    def __init__(self, fps_limit=8):
        # Variables para el majeno del tiempo
        self.fps_limit = fps_limit  # Limita los FPS
        self.last_processed_time = 0

        # Configuracion de mediapipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

        # Inicializamos la camara
        self.cap = cv2.VideoCapture(0)  

    # Función para detectar el parpadeo
    def detect_blink(self):
        # Obtenemos el tiempo actual
        current_time = time.time()

        # Solo procesamos un frame si ha pasado suficiente tiempo
        if current_time - self.last_processed_time < 1.0 / self.fps_limit:
            return False  # No procesar hasta que haya pasado el intervalo de tiempo
        
        ret, frame = self.cap.read()
        if not ret:
            return False
        
        # print(frame.shape) => (480, 640, 3)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame)

        blink_detected = False
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
                    blink_detected = True
        
        # Actualizamos el tiempo del procesamiento
        self.last_processed_time = current_time

        return blink_detected

    # Funcion que libera la camara cuando ya no se necesite
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
