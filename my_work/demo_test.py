from re import sub
import pytesseract
from cv2 import cv2
import json
import numpy as np



ratio1 = 860/662
ratio2 = 1039/799

dsize = (662, 799)



img = cv2.imread("/home/touhid/Desktop/gui_project/input/capture_15.png")



gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

result = 255 - thresh

subrect = result[int(6*ratio1):int(17*ratio1), int(546*ratio2):int(620*ratio2)]

text = pytesseract.image_to_string(subrect, lang='eng',config='--psm 10 ')

cv2.imwrite("/home/touhid/Desktop/gui_project/input/2.jpg", subrect)


print(text)