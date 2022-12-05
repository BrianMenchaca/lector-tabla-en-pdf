import cv2
import numpy as np
import re
import csv
import easyocr
import os

src = r"./tabla_origen.png"

if (os.path.exists("./img_prueba") == False):
    os.mkdir("./img_prueba")

################### PARTE 1 ###################
raw = cv2.imread(src, 1)
# Imagen en escala de grises
gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
cv2.imwrite("./img_prueba/tabla0.png", gray)

# Binarización de imagen
binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 35, -35)
# Mostrar imágenes
cv2.imwrite("./img_prueba/tabla1.png", binary)

################### PARTE 2 ###################
rows, cols = binary.shape
scale = 40
# Obtener adaptativamente el valor central
# Identifica la línea horizontal:
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
eroded = cv2.erode(binary, kernel, iterations=1)
dilated_col = cv2.dilate(eroded, kernel, iterations=1)
cv2.imwrite("./img_prueba/tabla2.png", dilated_col)

# Identificar la barra vertical:
scale = 20
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
eroded = cv2.erode(binary, kernel, iterations=1)
dilated_row = cv2.dilate(eroded, kernel, iterations=1)
cv2.imwrite("./img_prueba/tabla3.png", dilated_row)

# Combina las líneas horizontales y verticales reconocidas
bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)
cv2.imwrite("./img_prueba/tabla4.png", bitwise_and)

# Identificar el esquema de la tabla
merge = cv2.add(dilated_col, dilated_row)
cv2.imwrite("./img_prueba/tabla5.png", merge)

# Dos imágenes para restar, elimine el borde de la tabla
merge2 = cv2.subtract(binary, merge)
cv2.imwrite("./img_prueba/tabla6.png", merge2)

merge3 = cv2.add(merge2, bitwise_and)
cv2.imwrite("./img_prueba/tabla8.png", merge3)

################### PARTE 3 ###################
# Saca la marca de enfoque
ys, xs = np.where(bitwise_and > 0)

# Matriz de coordenadas horizontales y verticales
y_point_arr = []
x_point_arr = []

# Al ordenar, excluir píxeles similares, solo tome el último punto de valores similares.
# Este 10 es la distancia entre los dos píxeles, no es fijo, se ajustará de acuerdo con diferentes imágenes,
# básicamente la altura (salto de coordenadas y) y la longitud (salto de coordenadas x) de la tabla de celdas.
i = 0
sort_y_point = np.sort(ys)

for i in range(len(sort_y_point) - 1):
    if (sort_y_point[i + 1] - sort_y_point[i] > 10):
        y_point_arr.append(sort_y_point[i])
    i = i + 1
y_point_arr.append(sort_y_point[i])

# Coordenada y de bucle, tabla dividida de coordenadas x
data = [[] for i in range(len(y_point_arr))]

reader = easyocr.Reader(["es"], gpu=False)
print(xs)
print(y_point_arr)

j = 0
final_row = False

for i in range(len(xs) - 1):
    # Al dividir, el primer parámetro es la coordenada y, el segundo parámetro es la coordenada x
    if xs[i] > xs[i + 1]:
        j = j + 1
        continue

    # Verifica qe la distancia entre columnas sea mayor de 10 pixeles
    if xs[i + 1] - xs[i] < 10:
        continue

    if j == len(y_point_arr) - 1:
        # Si la ultima fila ya fue iterada, sale del for.
        if final_row:
            break
        else:
            j = j - 1
            final_row = True

    # Imprime coordenadas de la celda por pantalla
    print("tabla_final_" + str(j) + "-" + str(i) + ":", y_point_arr[j],
          y_point_arr[j + 1], xs[i], xs[i + 1])

    if final_row:
        dif = 0
    else:
        dif = y_point_arr[j + 1] - y_point_arr[j]

    cell = raw[y_point_arr[j] - dif:y_point_arr[j + 1] - dif, xs[i]:xs[i + 1]]
    cv2.imwrite("./img_prueba/tabla_final_" + str(j) + "-" + str(i) + ".png",
                cell)

    # Leer texto
    cv2.imwrite("./img_prueba/temp_img.png", cell)
    image = cv2.imread("./img_prueba/temp_img.png")
    text_list = reader.readtext(image, detail=0)

    # Convierte lista a string
    text1 = " ".join(text_list)

    # Eliminar caracteres especiales
    text1 = re.findall(r'[^\*"/:?\\|″′‖〈\n]', text1, re.S)
    text1 = "".join(text1)

    # Imprime la informacion de la celda por pantalla
    print('Información de imagen de celda:' + text1 + "\n")

    # Guarda el texto en la lista
    if final_row:
        data[j + 1].append(text1)
    else:
        data[j].append(text1)

####################### GRABA EN CSV #######################

# Escribo en CSV
# with open("./datos.csv", "w", newline='') as csv_file:
#     writer = csv.writer(csv_file, dialect='excel')
#     for index, item in enumerate(data):
#         print(index, ":", item)
# if index != len(data) - 1:
# writer.writerows([[item[0], item[1], item[2], item[3], item[4], item[5]]])

# Escribo en txt
with open("texto.txt", "w") as t:
    for index, item in enumerate(data):
        print(index, ":", item)
        t.write(str(item) + "\n")