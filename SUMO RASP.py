import cv2
import numpy as np
import gpiod
import time

# Configurar los pines GPIO
chip = gpiod.Chip('gpiochip0')

pin_izquierda = 17
izquierda = chip.get_line(pin_izquierda)
pin_centro = 27
centro = chip.get_line(pin_centro)
pin_derecha = 22
derecha = chip.get_line(pin_derecha)

izquierda.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
centro.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
derecha.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

def apagar_gpios():
    izquierda.set_value(0)
    centro.set_value(0)
    derecha.set_value(0)

def encontrar_contorno_con_mayor_cy(imagen, area_minima, x_roi, y_roi, w_roi, h_roi):
    roi = imagen[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    rango_bajo_rojo1 = np.array([0, 158, 222])
    rango_alto_rojo1 = np.array([69, 255, 255])
    mascara_rojo = cv2.inRange(hsv_roi, rango_bajo_rojo1, rango_alto_rojo1)

    contornos, _ = cv2.findContours(mascara_rojo, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_cy = -1
    contorno_seleccionado = None
    datos_contorno = None

    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > area_minima:
            momentos = cv2.moments(contorno)
            if momentos["m00"] != 0:
                cx = int(momentos["m10"] / momentos["m00"]) + x_roi
                cy = int(momentos["m01"] / momentos["m00"]) + y_roi
                if cy > max_cy:
                    max_cy = cy
                    contorno_seleccionado = contorno
                    datos_contorno = (cx, cy, area)

    if contorno_seleccionado is not None:
        x, y, w, h = cv2.boundingRect(contorno_seleccionado)
        cv2.rectangle(imagen, (x + x_roi, y + y_roi), (x + w + x_roi, y + h + y_roi), (0, 255, 0), 2)
        cv2.circle(imagen, (cx, cy), 5, (255, 0, 0), -1)

    return imagen, datos_contorno

# Iniciar captura de video
cap = cv2.VideoCapture(0)

# Configurar resolución baja para optimizar en Raspberry Pi
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

area_minima = 500
x_roi, y_roi, w_roi, h_roi = 100, 60, 120, 120
x1, x2 = 110, 210

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo recibir el fotograma. Salir...")
            break

        cv2.rectangle(frame, (x_roi, y_roi), (x_roi + w_roi, y_roi + h_roi), (255, 0, 0), 2)
        frame_procesado, datos_contorno = encontrar_contorno_con_mayor_cy(frame, area_minima, x_roi, y_roi, w_roi, h_roi)

        apagar_gpios()  # Asegurarse de que todos los GPIOs estén apagados antes de encender uno nuevo
        if datos_contorno:
            cx, cy, area = datos_contorno
            if cx < x1:
                izquierda.set_value(1)
                derecha.set_value(0)
                centro.set_value(0)
            elif cx > x2:
                izquierda.set_value(0)
                derecha.set_value(1)
                centro.set_value(0)
            else:
                izquierda.set_value(0)
                derecha.set_value(0)
                centro.set_value(1)

        cv2.imshow('Detector de objetos rojos en tiempo real', frame_procesado)

        if cv2.waitKey(1) == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    izquierda.release()
    centro.release()
    derecha.release()