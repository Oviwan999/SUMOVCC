import cv2
import numpy as np
import gpiod
import time
from picamera2 import Picamera2, MappedArray

# Configurar los pines GPIO
chip = gpiod.Chip('gpiochip4')


pin_izquierda = 17
izquierda = chip.get_line(pin_izquierda)
pin_centro = 27
centro = chip.get_line(pin_centro)
pin_derecha = 22
derecha = chip.get_line(pin_derecha)

izquierda.request(consumer="izq", type=gpiod.LINE_REQ_DIR_OUT)
centro.request(consumer="CTr", type=gpiod.LINE_REQ_DIR_OUT)
derecha.request(consumer="DR", type=gpiod.LINE_REQ_DIR_OUT)

def apagar_gpios():
    izquierda.set_value(0)
    centro.set_value(0)
    derecha.set_value(0)

def encontrar_contorno_con_mayor_cy( area_minima, x_roi, y_roi, w_roi, h_roi):
    frame = cap.capture_array()
    roi = frame[y_roi:y_roi+h_roi, x_roi:x_roi+w_roi]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    rango_bajo_rojo1 = np.array([0, 158, 222])
    rango_alto_rojo1 = np.array([69, 255, 255])
    rango_bajo_rojo2 = np.array([39, 212, 83])
    rango_alto_rojo2 = np.array([180, 255, 221])
    mascara1 = cv2.inRange(hsv_roi, rango_bajo_rojo1, rango_alto_rojo1)
    mascara2 = cv2.inRange(hsv_roi, rango_bajo_rojo2, rango_alto_rojo2)
    mascara_rojo = cv2.bitwise_or(mascara1, mascara2)
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
        cv2.rectangle(frame, (x + x_roi, y + y_roi), (x + w + x_roi, y + h + y_roi), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

    return frame, datos_contorno

# Iniciar captura de video
#cap = cv2.VideoCapture(0)
picam2 = Picamera2()
picam2.preview_configuration.main.size = (320,240)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
#picam2.start_preview(Preview.QTGL)
picam2.start()
cap=picam2

area_minima = 100
x_roi, y_roi, w_roi, h_roi = 30, 40, 320-50, 190
x1, x2 = 120, 180

try:
    while True:
        
        frame_procesado, datos_contorno = encontrar_contorno_con_mayor_cy(area_minima, x_roi, y_roi, w_roi, h_roi)
        cv2.rectangle(frame_procesado, (x_roi, y_roi), (x_roi + w_roi, y_roi + h_roi), (255, 0, 0), 2)
        cv2.line(frame_procesado, (x1, 0), (x1, 240), (255, 255, 255), 2)
        cv2.line(frame_procesado, (x2, 0), (x2, 240), (255, 255, 255), 2)
        apagar_gpios()

        apagar_gpios()  # Asegurarse de que todos los GPIOs estén apagados antes de encender uno nuevo
        if datos_contorno:
            cx, cy, area = datos_contorno
            if cx < x1:
                izquierda.set_value(1)
                #derecha.set_value(0)
                #centro.set_value(0)
                print("izquierda")
            elif cx > x2:
                #izquierda.set_value(0)
                derecha.set_value(1)
                #centro.set_value(0)
                print("derecha")
            else:
                #izquierda.set_value(0)
                #derecha.set_value(0)
                centro.set_value(1)
                print("centro")

        cv2.imshow('Detector de objetos rojos en tiempo real', frame_procesado)

        if cv2.waitKey(1) == ord('q'):
            break
finally:
    cap.stop()
    apagar_gpios()
    izquierda.release()
    centro.release()
    derecha.release()
    cv2.destroyAllWindows()
