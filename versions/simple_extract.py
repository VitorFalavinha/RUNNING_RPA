import cv2
import pytesseract
from PIL import Image
import os

# Abre a imagem
img = Image.open(r"imagens_corrida\recorte_1745978618905.jpg")

# Recorta a área onde está o número 4.00 (ajuste os valores conforme necessário)
# box = (esquerda, topo, direita, fundo)
crop_box = (240, 150, 620, 270)
cropped_img = img.crop(crop_box)

# Força OCR apenas na região recortada
text = pytesseract.image_to_string(cropped_img, config='--psm 7')
print("Valor extraído:", text)


# texto = pytesseract.image_to_string(Image.open(r'imagens_corrida\recorte_1745978618905.jpg'), lang='eng')
#print("Texto extraído:")
#print(texto) 


