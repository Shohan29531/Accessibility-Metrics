import json
from cv2 import cv2
import numpy as np
import imutils

with open('capture_15.json') as f:
  capture_15_data = json.load(f)

with open('capture_16.json') as f:
  capture_16_data = json.load(f)  


#read data from json file

rects_in_capture_15=capture_15_data["compos"]
rects_in_capture_16=capture_16_data["compos"]
    
def is_same_rectangle(rect1, rect2):

    if(rect1["row_min"]==rect2["row_min"] and rect1["row_max"]==rect2["row_max"]
     and rect1["column_min"]==rect2["column_min"] and rect1["column_max"]==rect2["column_max"]):
        return True

    return False

def is_big_rect(rect, dsize):
    (sizex, sizey) = dsize
    if(rect[4]==sizex and rect[5]==sizey):
        return True

    return False    


#find similar rectangles in both imageas and add an is_same attribute

sim=0
for i in range(len(rects_in_capture_15)):
    for j in range(len(rects_in_capture_16)):
        if "is_same" in rects_in_capture_16[j].keys():
            if(rects_in_capture_16[j]["is_same"]):
                continue
            
        if(is_same_rectangle(rects_in_capture_15[i], rects_in_capture_16[j])):
            sim+=1
            rects_in_capture_15[i]["is_same"]=True
            rects_in_capture_16[j]["is_same"]=True
            break
        else:
            rects_in_capture_15[i]["is_same"]=False
            rects_in_capture_16[j]["is_same"]=False           




all_diff_rects = []

#save a file with the difference rects marked

im = cv2.imread('capture_15.png')
#because UIED outputs an image of this size
dsize=(999,827)
im = cv2.resize(im, dsize)

for rectangle in rects_in_capture_15:
    if(rectangle["is_same"]):
        continue
    cv2.rectangle(im,(rectangle["column_min"],rectangle["row_min"]),
    (rectangle["column_max"],rectangle["row_max"]),(0,255,0),2)

    temp = [rectangle["column_min"], rectangle["row_min"], rectangle["column_max"], rectangle["row_max"],
     (rectangle["column_max"]-rectangle["column_min"]),
     (rectangle["row_max"]-rectangle["row_min"])]

    all_diff_rects.append(temp)


cv2.imwrite("capture_15_with_rects_diff.png", im)




#save another file with the difference rects marked

im2 = cv2.imread('capture_16.png')
dsize=(999,827)
im2 = cv2.resize(im2, dsize)

for rectangle in rects_in_capture_16:
    if(rectangle["is_same"]):
        continue
    cv2.rectangle(im2,(rectangle["column_min"],rectangle["row_min"]),
    (rectangle["column_max"],rectangle["row_max"]),(0,255,0),2)

    temp = [rectangle["column_min"], rectangle["row_min"], rectangle["column_max"], rectangle["row_max"],
     (rectangle["column_max"]-rectangle["column_min"]),
     (rectangle["row_max"]-rectangle["row_min"])]
     
    all_diff_rects.append(temp)

cv2.imwrite("capture_16_with_rects_diff.png", im2)

vis = np.concatenate((im, im2), axis=1)
cv2.imwrite('diff.png', vis)






#save a file with the same rects marked

im = cv2.imread('capture_15.png')
dsize=(999,827)
im = cv2.resize(im, dsize)

for rectangle in rects_in_capture_15:
    if(rectangle["is_same"]==False):
        continue
    cv2.rectangle(im,(rectangle["column_min"],rectangle["row_min"]),
    (rectangle["column_max"],rectangle["row_max"]),(0,255,0),2)

cv2.imwrite("capture_15_with_rects_sim.png", im)





#save another file with the same rects marked

im2 = cv2.imread('capture_16.png')
dsize=(999,827)
im2 = cv2.resize(im2, dsize)

for rectangle in rects_in_capture_16:
    if(rectangle["is_same"]==False):
        continue
    cv2.rectangle(im2,(rectangle["column_min"],rectangle["row_min"]),
    (rectangle["column_max"],rectangle["row_max"]),(0,255,0),2)


cv2.imwrite("capture_16_with_rects_sim.png", im2)

vis = np.concatenate((im, im2), axis=1)
cv2.imwrite('sim.png', vis)












#image diff calculator using opencv

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
dsize=(999,827)
original = cv2.resize(original,dsize)
duplicate = cv2.imread("capture_16.png")
duplicate = cv2.resize(duplicate, dsize)


difference = diff_image(duplicate, original)

cv2.imwrite("diff_15_16.png", difference)


image_diff = cv2.imread('diff_15_16.png')
imgray = cv2.cvtColor(image_diff, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray,0, 255, cv2.THRESH_BINARY_INV)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



file= open("bounding_rectangles.txt", "w")

for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if(w<=1 or h<=1):
        continue
    cv2.rectangle(image_diff,(x,y),(x+w,y+h),(0,255,0),2)
    
    temp=[x,y,x+w,y+h,w,h]
    all_diff_rects.append(temp)

    #print(x,y,x+w,y+h,w,h)
    line = str(x) + " " + str(y) + " " + str(x+w) + " " + str(y+h) +" " + str(w) + " "+ str(h) + "\n"
    file.write(line)


    
cv2.imshow('img',image_diff)

cv2.imwrite("diff_15_16_with_rects.png", image_diff)




#incorporate the image_diff rectangles in the diff.png image

im = cv2.imread('capture_15.png')
dsize=(999,827)
im = cv2.resize(im, dsize)

im2 = cv2.imread('capture_16.png')
dsize=(999,827)
im2 = cv2.resize(im2, dsize)


for diff_rect in all_diff_rects:

    if(is_big_rect(diff_rect,dsize)):
        continue
    
    print(diff_rect)

    cv2.rectangle(im,(diff_rect[0],diff_rect[1]),(diff_rect[2],diff_rect[3]),(0,255,0),2)
    cv2.rectangle(im2,(diff_rect[0],diff_rect[1]),(diff_rect[2],diff_rect[3]),(0,255,0),2)

cv2.imwrite("capture_15_with_all_diff.png",im)
cv2.imwrite("capture_16_with_all_diff.png",im2)


vis = np.concatenate((im, im2), axis=1)
cv2.imwrite('diff_all_rects.png', vis)

