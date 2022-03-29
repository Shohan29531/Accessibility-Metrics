from re import sub
import pytesseract
from cv2 import cv2
import json
import numpy as np
import os

notepad_dom = False

print("starting sub-image extraction")

dsize = (662, 799)

ratio1 = 860/dsize[0]
ratio2 = 1039/dsize[1]


if notepad_dom:
    dsize = (497, 798)
    ratio1 = 606/dsize[0]
    ratio2 = 974/dsize[1]

input_directory = '/home/touhid/Desktop/gui_project/input/'
input_json_directory = '/home/touhid/Desktop/gui_project/data/output/'

input_image_file_names = os.listdir(input_directory)

input_image_file_names.sort()

input_filenames_without_extension = []

for input_img in input_image_file_names:
    temp = input_img.split('.')
    input_filenames_without_extension.append(temp[0])


input_filenames_bak = input_image_file_names    
input_image_file_names = []

for input_img in input_filenames_bak:
    input_image_file_names.append(input_directory + input_img)


input_json_file_names=[]

for i in range(len(input_image_file_names)):
    fn = input_json_directory + input_filenames_without_extension[i] + '/ocr/' + input_filenames_without_extension[i] + '.json'
    input_json_file_names.append(fn)



for i in range(len(input_image_file_names)):
    img = cv2.imread(input_image_file_names[i])


    jsonfilepath = input_json_file_names[i]

    with open(jsonfilepath) as json_file:
        data = json.load(json_file)['compos']

    bias = 3

    j=1
    for entry in data:

        row_min = entry['row_min'] -bias
        row_max = entry['row_max'] + bias
        column_min = entry['column_min'] - bias
        column_max = entry['column_max'] + bias


        if column_min<0:
            column_min = 0
        if row_min<0:
            row_min = 0
        if column_max > 799:
            column_max = 799 
        if row_max > 662:
            row_max =662           


        filename = "/home/touhid/Desktop/gui_project/ocr_input/" + input_filenames_without_extension[i] + "/" 

        if not os.path.exists(filename):
            os.makedirs(filename)

        filename = filename + str(j) + ".jpg"    

        # print(filename)
        subrect = img[int(row_min*ratio1):int(row_max*ratio1), int(column_min*ratio2):int(column_max*ratio2)]
        cv2.imwrite(filename, subrect)

        j+=1



print("ending sub-image extraction")