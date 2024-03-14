import cv2
import numpy as np

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

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

area_minima = 500
x_roi, y_roi, w_roi, h_roi = 100, 100, 400, 300
x1, x2 = 200, 400

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo recibir el fotograma. Salir...")
        break

    cv2.rectangle(frame, (x_roi, y_roi), (x_roi + w_roi, y_roi + h_roi), (255, 0, 0), 2)
    frame_procesado, datos_contorno = encontrar_contorno_con_mayor_cy(frame, area_minima, x_roi, y_roi, w_roi, h_roi)

    altura = frame_procesado.shape[0]
    cv2.line(frame_procesado, (x1, 0), (x1, altura), (255, 255, 255), 2)
    cv2.line(frame_procesado, (x2, 0), (x2, altura), (255, 255, 255), 2)
    cv2.imshow('Detector de objetos rojos en tiempo real', frame_procesado)

    pantalla_datos = np.zeros((500, 500, 3), dtype=np.uint8)
    if datos_contorno:
        cx, cy, area = datos_contorno
        texto = f"Centro: ({cx}, {cy}), Area: {area}"
        if cx < x1:
            texto += " | Izquierda"
        elif cx > x2:
            texto += " | Derecha"
        else:
            texto += " | Centro"

        cv2.putText(pantalla_datos, texto, (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('Datos del Contorno', pantalla_datos)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
|