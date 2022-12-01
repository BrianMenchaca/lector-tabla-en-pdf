import cv2
import numpy as np
import matplotlib.pyplot as plt

file =  r'./img/factura/factura0.jpg'

im1 = cv2.imread(file, 0)
im = cv2.imread(file)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

thresh,img_bin = cv2.threshold(im1,128,255,cv2.THRESH_BINARY)
img_bin = 255-img_bin
# plotting = plt.imshow(img_bin,cmap='gray')
# plt.title("Inverted Image with global thresh holding")
# plt.show()

vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, np.array(im1).shape[1]//150))
eroded_image = cv2.erode(img_bin, vertical_kernel, iterations=5)
vertical_lines = cv2.dilate(eroded_image, vertical_kernel, iterations=5)

hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (np.array(im1).shape[1]//150, 1))
image_2 = cv2.erode(img_bin, hor_kernel, iterations=5)
horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=5)

vertical_horizontal_lines = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
vertical_horizontal_lines = cv2.erode(~vertical_horizontal_lines, kernel, iterations=3)

thresh, vertical_horizontal_lines = cv2.threshold(vertical_horizontal_lines,128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
b_image = cv2.bitwise_not(cv2.bitwise_xor(im1,vertical_horizontal_lines))
cv2.imwrite("tabla.jpg", b_image)
plotting = plt.imshow(b_image,cmap='gray')
plt.show()



# ret,thresh_value = cv2.threshold(im1,180,255,cv2.THRESH_BINARY_INV)

# kernel = np.ones((5,5),np.uint8)
# dilated_value = cv2.dilate(thresh_value,kernel,iterations = 1)

# contours, hierarchy = cv2.findContours(dilated_value,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
# cordinates = []
# for cnt in contours:
#     x,y,w,h = cv2.boundingRect(cnt)
#     cordinates.append((x,y,w,h))
#     #bounding the images
#     if y< 50:
        
#         cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),1)
        
# plt.imshow(im)
# cv2.namedWindow('detecttable', cv2.WINDOW_NORMAL)
# cv2.imwrite('detecttable.jpg',im)