# -*- coding: utf-8 -*-
import cv2
import pytesseract
import numpy as np


class ImageTableOCR(object):

    # Inicializar
    def __init__(self, ImagePath):
        # Leer foto
        self.image = cv2.imread(ImagePath, 1)
        # Convertir la imagen al modo de escala de grises
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    # Detección de línea horizontal
    def HorizontalLineDetect(self):

        # Binarización de imagen
        ret, thresh1 = cv2.threshold(self.gray, 240, 255, cv2.THRESH_BINARY)
        # Realizar dos filtros de mediana
        blur = cv2.medianBlur(thresh1, 3)  # Tamaño de plantilla 3 * 3
        blur = cv2.medianBlur(blur, 3)  # Tamaño de plantilla 3 * 3

        h, w = self.gray.shape

        # Lista de líneas horizontales
        horizontal_lines = []
        for i in range(h - 1):
            # Encuentre el segmento de línea divisoria de dos registros, la diferencia de píxeles promedio entre dos líneas adyacentes es mayor que 120
            if abs(np.mean(blur[i, :]) - np.mean(blur[i + 1, :])) > 120:
                # Dibuja segmentos de línea en la imagen
                horizontal_lines.append([0, i, w, i])
                cv2.line(self.image, (0, i), (w, i), (0, 255, 0), 2)

        horizontal_lines = horizontal_lines[1:]
        # print(horizontal_lines)
        return horizontal_lines

    # Detección de línea recta longitudinal
    def VerticalLineDetect(self):
        # Detección de bordes canny
        edges = cv2.Canny(self.gray, 30, 240)

        # Detección de línea de Hough
        minLineLength = 500
        maxLineGap = 30
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100,
                                minLineLength, maxLineGap).tolist()
        # lines.append([[13, 937, 13, 102]])
        # lines.append([[756, 937, 756, 102]])
        sorted_lines = sorted(lines, key=lambda x: x[0])

        # Lista de líneas verticales
        vertical_lines = []
        for line in sorted_lines:
            for x1, y1, x2, y2 in line:
                # Dibuja líneas verticales en la imagen
                if x1 == x2:
                    # print(line)
                    vertical_lines.append((x1, y1, x2, y2))
                    cv2.line(self.image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        return vertical_lines

    # Detección de vértices
    def VertexDetect(self):
        vertical_lines = self.VerticalLineDetect()
        horizontal_lines = self.HorizontalLineDetect()

        # Lista de vértices
        vertex = []
        for v_line in vertical_lines:
            for h_line in horizontal_lines:
                vertex.append((v_line[0], h_line[1]))

        # print(vertex)

        # Dibujar vértice
        for point in vertex:
            cv2.circle(self.image, point, 1, (255, 0, 0), 2)

        return vertex

    # Buscar rango de celdas
    def CellDetect(self):
        vertical_lines = self.VerticalLineDetect()
        horizontal_lines = self.HorizontalLineDetect()

        # Lista de vértices
        rects = []
        for i in range(0, len(vertical_lines) - 1, 2):
            for j in range(len(horizontal_lines) - 1):
                rects.append((vertical_lines[i][0], horizontal_lines[j][1], \
                              vertical_lines[i + 1][0], horizontal_lines[j + 1][1]))

        # print(rects)
        return rects


    # Identifica el texto en la celda
    def OCR(self):
        rects = self.CellDetect()
        thresh = self.gray

        # Lista de caracteres especiales
        special_char_list = ' `~!@#$%^&*()-_=+[]{}|\\;:‘’，。《》/？ˇ'
        for i in range(20):
            rect1 = rects[i]
            DetectImage1 = thresh[rect1[1]:rect1[3], rect1[0]:rect1[2]]

            # La ruta donde se encuentra Tesseract
            pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR/tesseract.exe'

            # Número de identificación (primera columna de cada fila)
            text1 = pytesseract.image_to_string(
                DetectImage1, config="--psm 10")
            print(text1, end='-->')

    # Mostrar imagen
    def ShowImage(self):
        # cv2.imshow('AI', self.image)
        cv2.waitKey(0)
        cv2.imwrite('./Horizontal.png', self.image)

ImagePath = './img/factura/factura0.jpg'
imageOCR = ImageTableOCR(ImagePath)
imageOCR.OCR()
imageOCR.ShowImage()