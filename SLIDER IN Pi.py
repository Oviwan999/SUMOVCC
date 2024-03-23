import cv2
import numpy as np
from picamera2 import Picamera2,MappedArray, Preview

def callback(x):
    pass
    
picam2 = Picamera2()
picam2.preview_configuration.main.size = (320,240)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
#picam2.start_preview(Preview.QTGL)
picam2.start()


# Crear una ventana para los deslizadores (sliders) de OpenCV
cv2.namedWindow('Ajustes de color rojo')
cv2.createTrackbar('Hue Min', 'Ajustes de color rojo', 0, 180, callback)
cv2.createTrackbar('Hue Max', 'Ajustes de color rojo', 10, 180, callback)
cv2.createTrackbar('Sat Min', 'Ajustes de color rojo', 100, 255, callback)
cv2.createTrackbar('Sat Max', 'Ajustes de color rojo', 255, 255, callback)
cv2.createTrackbar('Val Min', 'Ajustes de color rojo', 100, 255, callback)
cv2.createTrackbar('Val Max', 'Ajustes de color rojo', 255, 255, callback)

while True:
    frame = picam2.capture_array()
    
    # Convertir la imagen a HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    # Leer los valores de los deslizadores
    h_min = cv2.getTrackbarPos('Hue Min', 'Ajustes de color rojo')
    h_max = cv2.getTrackbarPos('Hue Max', 'Ajustes de color rojo')
    s_min = cv2.getTrackbarPos('Sat Min', 'Ajustes de color rojo')
    s_max = cv2.getTrackbarPos('Sat Max', 'Ajustes de color rojo')
    v_min = cv2.getTrackbarPos('Val Min', 'Ajustes de color rojo')
    v_max = cv2.getTrackbarPos('Val Max', 'Ajustes de color rojo')
    
    # Crear la mascara de color rojo basada en los valores de los deslizadores
    lower_red = np.array([h_min, s_min, v_min])
    upper_red = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # Aplicar la mascara sobre la imagen original
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Mostrar el resultado
    cv2.imshow('Original', frame)
    #cv2.imshow('Original2', hsv)
    #cv2.imshow('Mascara de color rojo', mask)
    cv2.imshow('Resultado', result)
    
    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Limpieza
picam2.stop()
cv2.destroyAllWindows()
