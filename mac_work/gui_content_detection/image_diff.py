from cv2 import cv2
import numpy as np 

import imutils

def diff_image(img2, img1):
    rows2= img2.shape[0]
    cols2= img2.shape[1] 

    new_img = img2
    for i in range(rows2):
      for j in range(cols2):
         pixel2 = img2[i,j]
         pixel1 = img1[i,j]

         if(pixel2[0]==pixel1[0] and pixel2[1]==pixel1[1] and pixel2[2]==pixel1[2]):  
             new_img[i,j]=0
         else:
             new_img[i,j]=img2[i,j]    
    
    return new_img



original = cv2.imread("capture_15.png")
duplicate = cv2.imread("capture_16.png")


difference = diff_image(duplicate, original)

cv2.imwrite("diff_15_16.png", difference)


im = cv2.imread('diff_15_16.png')
imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray,0, 255, cv2.THRESH_BINARY_INV)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



file= open("bounding_rectangles.txt", "w")

for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if(w<=1 or h<=1):
        continue
    cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)


    print(x,y,x+w,y+h,w,h)
    line = str(x) + " " + str(y) + " " + str(x+w) + " " + str(y+h) +" " + str(w) + " "+ str(h) + "\n"
    file.write(line)


    
cv2.imshow('img',im)

cv2.imwrite("diff_15_16_with_rects.png", im)

         

    
