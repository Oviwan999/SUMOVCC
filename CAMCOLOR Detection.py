import cv2
import numpy as np


def encontrar_contorno_con_mayor_cy(imagen, area_minima):
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    rango_bajo_rojo1 = np.array([0, 158, 222])
    rango_alto_rojo1 = np.array([69, 255, 255])
    rango_bajo_rojo2 = np.array([39, 212, 83])
    rango_alto_rojo2 = np.array([180, 255, 221])
    mascara1 = cv2.inRange(hsv, rango_bajo_rojo1, rango_alto_rojo1)
    mascara2 = cv2.inRange(hsv, rango_bajo_rojo2, rango_alto_rojo2)
    mascara_rojo = cv2.bitwise_or(mascara1, mascara2)

    # Crear la máscara de color rojo basada en los valores de los deslizadores
    # lower_red = np.array([0, 158, 122])
    # upper_red = np.array([69, 255, 255])
    # mask = cv2.inRange(hsv, lower_red, upper_red)

    # Aplicar la máscara sobre la imagen original
    # mascara_rojo = cv2.bitwise_and(frame, frame, mask=mask)

    contornos, _ = cv2.findContours(mascara_rojo, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_cy = -1
    contorno_seleccionado = None
    datos_contorno = None

    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > area_minima:
            momentos = cv2.moments(contorno)
            if momentos["m00"] != 0:
                cx = int(momentos["m10"] / momentos["m00"])
                cy = int(momentos["m01"] / momentos["m00"])
                if cy > max_cy:
                    max_cy = cy
                    contorno_seleccionado = contorno
                    datos_contorno = (cx, cy, area)

    if contorno_seleccionado is not None:
        x, y, w, h = cv2.boundingRect(contorno_seleccionado)
        cv2.rectangle(imagen, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(imagen, (cx, cy), 5, (255, 255, 255), -1)

    return imagen, datos_contorno


# Iniciar captura de video
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

area_minima = 500  # Define aquí el área mínima para los contornos

while True:
    # Capturar fotograma por fotograma
    ret, frame = cap.read()

    # Si el fotograma es leído correctamente ret es True
    if not ret:
        print("No se pudo recibir el fotograma. Salir...")
        break

    # Procesar el fotograma
    frame_procesado, datos_contorno = encontrar_contorno_con_mayor_cy(frame, area_minima)
    x1,x2 = 200,400
    # Mostrar el fotograma procesado
    altura = frame_procesado.shape[0]  # Obtener la altura de la imagen
    cv2.line(frame_procesado, (x1, 0), (x1, altura), (255, 255, 255), 2)
    cv2.line(frame_procesado, (x2, 0), (x2, altura), (255, 255, 255), 2)
    cv2.imshow('Detector de objetos rojos en tiempo real', frame_procesado)

    # Preparar y mostrar los datos del contorno seleccionado en otra ventana
    pantalla_datos = np.zeros((500, 500, 3), dtype=np.uint8)
    if datos_contorno:
        cx, cy, area = datos_contorno
        texto = f"Centro: ({cx}, {cy}), Area: {area}"
        if cx < x1:
            texto = "Objeto a la derecha \n"+texto
        elif cx > x2:
            texto = "Objeto a la izquierda \n"+ texto
        else:
            texto = "Objeto centrado \n"+texto

        cv2.putText(pantalla_datos, texto, (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('Datos del Contorno', pantalla_datos)

    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) == ord('q'):
        break

## liberar la captura ##
cap.release()
cv2.destroyAllWindows()

