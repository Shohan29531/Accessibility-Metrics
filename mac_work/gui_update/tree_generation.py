import json
from cv2 import cv2
import numpy as np
import imutils
import math
from treelib import Node, Tree

from sklearn import tree
import graphviz
import random

with open('capture_15.json') as f:
  capture_15_data = json.load(f)

with open('capture_16.json') as f:
  capture_16_data = json.load(f)  

#read data from json file



def is_big_rect(rect, dsize):
    (sizex, sizey) = dsize
    if(rect[4]==sizex and rect[5]==sizey):
        return True

    return False   




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

diff_rects_opencv=[]


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



for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(image_diff,(x,y),(x+w,y+h),(0,255,0),2)
    
    temp=[x,y,x+w,y+h,w,h]
    diff_rects_opencv.append(temp)









all_rect_dictionary=dict()

all_rect_list=[]

rects_in_image=dict()

capture_15_ID='0'
capture_16_ID='1'

rects_in_image[capture_15_ID]=[]
rects_in_image[capture_16_ID]=[]


rects_in_capture_15=capture_15_data["compos"]
rects_in_capture_16=capture_16_data["compos"]



def is_inside(small, big):

    sum=0

    if(small[0]<big[0]):
        return False
    else:
        sum+=(small[0]-big[0])

    if(small[1]<big[1]):
        return False
    else:
        sum+=(small[1]-big[1])

    if(small[2]>big[2]):
        return False
    else:
        sum+=(big[2]-small[2]) 

    if(small[3]>big[3]):
        return False
    else:
        sum+=(big[3]-small[3]) 

    if(sum<=0):
        return False
    return True    



for rect in rects_in_capture_15:
    temp=[rect['column_min'], rect['row_min'], rect['column_max'], rect['row_max'],
     (rect['column_max']-rect['column_min']),(rect['row_max']-rect['row_min'])]

    temp_str = str(temp)

    if(temp_str in all_rect_dictionary):
        index = all_rect_dictionary[temp_str]
        if(index not in rects_in_image[capture_15_ID]):
            rects_in_image[capture_15_ID].append(index)      
        continue
    else:
        print(temp)
        all_rect_list.append(temp)
        index=len(all_rect_dictionary)
        all_rect_dictionary[temp_str]=index
        rects_in_image[capture_15_ID].append(index)

print()

for rect in rects_in_capture_16:
    temp=[rect['column_min'], rect['row_min'], rect['column_max'], rect['row_max'],
     (rect['column_max']-rect['column_min']),(rect['row_max']-rect['row_min'])]

    temp_str = str(temp)

    if(temp_str in all_rect_dictionary):
        index = all_rect_dictionary[temp_str]
        if(index not in rects_in_image[capture_16_ID]):
            rects_in_image[capture_16_ID].append(index)  
        continue
    else:
        print(temp)
        all_rect_list.append(temp)
        index=len(all_rect_dictionary)
        all_rect_dictionary[temp_str]=index  
        rects_in_image[capture_16_ID].append(index)  

print()

for diff_rect in diff_rects_opencv:
    if(is_big_rect(diff_rect,(999,827))):
        continue

    print(diff_rect)
    all_rect_list.append(diff_rect)
    index=len(all_rect_dictionary)
    all_rect_dictionary[str(diff_rect)]=index
    rects_in_image[capture_16_ID].append(index)







tree_structure=dict()

for rect1 in all_rect_list:
    for rect2 in all_rect_list:
        if(is_inside(rect2, rect1)):
            index=all_rect_dictionary[str(rect1)]

            if(str(index) in tree_structure):
                tree_structure[str(index)].append(all_rect_dictionary[str(rect2)])
            else:
                tree_structure[str(index)]=[all_rect_dictionary[str(rect2)]]    

print(tree_structure)








img = np.zeros((827,999,3),np.uint8)


for x in range(827):
    for y in range(999):
        value = random.randint(0,1)
        if value == 1:
            img[x,y] = [0,0,0]

cv2.imwrite("black.png",img)



   
#img = cv2.imread("capture_16.png")
img = cv2.resize(img, dsize)

for diff_rect in all_rect_list:
    if(is_big_rect(diff_rect,dsize)):
        continue

    cv2.rectangle(img,(diff_rect[0],diff_rect[1]),(diff_rect[2],diff_rect[3]),(0,255,0),1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (math.floor((diff_rect[0]+diff_rect[2])/2),math.floor((diff_rect[1]+diff_rect[3])/2))
    #org=(diff_rect[0],diff_rect[1])

    fontScale = 0.4
    color = (255, 0, 255)
    thickness = 1

    image = cv2.putText(img, str(all_rect_dictionary[str(diff_rect)]), org, font, 
                    fontScale, color, thickness, cv2.LINE_AA)    


    


cv2.imwrite("diff_with_numbered_rects_black.png",img)


