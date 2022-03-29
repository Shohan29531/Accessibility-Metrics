from re import sub
import pytesseract
from cv2 import cv2
import json
import numpy as np
from background_detection import BackgroundColorDetector
from autocorrect import Speller
import os

notepad_dom = False

print("starting ocr")

spell = Speller(lang='en')
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

    new_data = []

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
            row_max = 662           

        #print(i)

        filename_input = "/home/touhid/Desktop/gui_project/ocr_input/" + input_filenames_without_extension[i] + '/' + str(j) + ".jpg"
        filename_output = "/home/touhid/Desktop/gui_project/ocr_output/" + input_filenames_without_extension[i] + '/'
        filename_output_dir = filename_output

        is_white_background = False
        BackgroundColor = BackgroundColorDetector(filename_input)
        color = BackgroundColor.detect_and_round()

        if(color[0] > 160 and color[1] > 160 and color[2] > 160):
            is_white_background = True

        #print(color, is_white_background)

        if is_white_background == True:

            subrect = img[int(row_min*ratio1):int(row_max*ratio1), int(column_min*ratio2):int(column_max*ratio2)]
            text = pytesseract.image_to_string(subrect, lang='eng',config='--psm 10 ')

            if not os.path.exists(filename_output):
                os.makedirs(filename_output)

            filename_output = filename_output + str(j) + ".jpg"   

            cv2.imwrite(filename_output, subrect)

        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #blur = cv2.GaussianBlur(gray, (3,3), 0)

            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            result = 255 - thresh 
            subrect = result[int(row_min*ratio1):int(row_max*ratio1), int(column_min*ratio2):int(column_max*ratio2)]
            text = pytesseract.image_to_string(subrect, lang='eng',config='--psm 10 ')

            if not os.path.exists(filename_output):
                os.makedirs(filename_output)

            filename_output = filename_output + str(j) + ".jpg"             
            cv2.imwrite(filename_output, subrect)


        #print(int(row_min*ratio1), int(row_max*ratio1), int(column_min*ratio2), int(column_max*ratio2))

        

        text = text.strip('\n\f')

        corrected_text = spell(text)

        corrected_text = corrected_text.strip('\n\f')

        #print(text, corrected_text)

        entry['text'] = text
        entry['spell_corrected_text'] = corrected_text
        entry['id'] = j

        new_data.append(entry)


        j+=1


    json_data = {"compos" : new_data}

    with open(filename_output_dir + input_filenames_without_extension[i] + '.json', 'w') as files:
        json.dump(json_data, files, indent=4, sort_keys=True)


print("ending ocr")