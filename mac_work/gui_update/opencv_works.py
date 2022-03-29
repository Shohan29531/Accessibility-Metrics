import json
from cv2 import cv2
import numpy as np
import imutils
import math
from treelib import Node, Tree

from sklearn import tree
import graphviz
import random
import xml.etree.ElementTree as gfg 
import lxml.etree as etree


dsize = (999,827)


def transformCoordinates(rect, given_size):
    col_scale = (given_size[0]*1.0)/(dsize[0]*1.0)
    row_scale = (given_size[1]*1.0)/(dsize[1]*1.0)

    col_min = int(round(rect[0]*col_scale, 0))
    col_max = int(round(rect[2]*col_scale, 0))

    row_min = int(round(rect[1]*row_scale, 0))
    row_max = int(round(rect[3]*row_scale, 0))

    width = col_max - col_min
    height = row_max - row_min

    return [col_min, row_min, col_max, row_max, width, height]



 


def is_same_rectangle(rect1, rect2):

    if(rect1["row_min"]==rect2["row_min"] and rect1["row_max"]==rect2["row_max"]
     and rect1["column_min"]==rect2["column_min"] and rect1["column_max"]==rect2["column_max"]):
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


def is_big_rect(rect, dsize):
    (sizex, sizey) = dsize
    if(rect[4]==sizex and rect[5]==sizey):
        return True

    return False   


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


def get_diff_rects_via_opencv(img2_name, img1_name):

    diff_rects_opencv=[]
    
    first_image = cv2.imread(img1_name)
    first_image = cv2.resize(first_image, dsize)

    second_image = cv2.imread(img2_name)
    second_image = cv2.resize(second_image, dsize)

    diff_opencv = diff_image(second_image, first_image)

    imgray = cv2.cvtColor(diff_opencv, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray,0, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(diff_opencv,(x,y),(x+w,y+h),(0,255,0),2)
        
        temp=[x,y,x+w,y+h,w,h]
        diff_rects_opencv.append(temp)

    return diff_rects_opencv