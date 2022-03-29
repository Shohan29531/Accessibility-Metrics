import json
import os
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


notepad_dom = False
## Define the image size
## Using the same size as UIED output images
dsize = (799,662)

dsize_cameron = (1039, 860)
## Utility Methods

if notepad_dom:
    dsize = (798, 497)

tolerance = 5
neg_tolerance = -5

iou_threshold = 0.5


print("starting opencv analysis")

'''

Courtesy:
https://gist.github.com/reimund/5435343/

'''

def dict2xml(d, root_node=None):
	wrap          =     False if None == root_node or isinstance(d, list) else True
	root          = 'objects' if None == root_node else root_node
	root_singular = root[:-1] if 's' == root[-1] and None == root_node else root
	xml           = ''
	children      = []

	if isinstance(d, dict):
		for key, value in dict.items(d):
			if isinstance(value, dict):
				children.append(dict2xml(value, key))
			elif isinstance(value, list):
				children.append(dict2xml(value, key))
			else:
				xml = xml + ' ' + key + '="' + str(value) + '"'
	else:
		for value in d:
			children.append(dict2xml(value, root_singular))

	end_tag = '>' if 0 < len(children) else '/>'

	if wrap or isinstance(d, dict):
		xml = '<' + root + xml + end_tag

	if 0 < len(children):
		for child in children:
			xml = xml + child

		if wrap or isinstance(d, dict):
			xml = xml + '</' + root + '>'

	return xml



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




def bb_intersection_over_union(boxA, boxB):

	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])

	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

	iou = interArea / float(boxAArea + boxBArea - interArea)

	return iou


def is_same_rectangle(rect1, rect2):

    '''
    val1 = abs(rect1["row_min"] - rect2["row_min"])
    val2 = abs(rect1["row_max"] - rect2["row_max"])

    val3 = abs(rect1["column_min"] - rect2["column_min"])
    val4 = abs(rect1["column_max"] - rect2["column_max"])

    if val1 <=tolerance and val2 <=tolerance and val3 <=tolerance and val4 <=tolerance:
        return True

    return False
    '''

    boxA = [rect1["column_min"], rect1["row_min"], rect1["column_max"], rect1["row_max"]]
    boxB = [rect2["column_min"], rect2["row_min"], rect2["column_max"], rect2["row_max"]]

    if bb_intersection_over_union(boxA, boxB) >= iou_threshold:
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

    acceptable_errors = 0

    v1=(small[0]-big[0])

    v2=(small[1]-big[1])

    v3=(big[2]-small[2])

    v4=(big[3]-small[3])


    if v1 < 0:
        if v1 >= neg_tolerance:
            acceptable_errors += 1
        else:
            return False

    if v2 < 0:
        if v2 >= neg_tolerance:
            acceptable_errors += 1
        else:
            return False


    if v3 < 0:
        if v3 >= neg_tolerance:
            acceptable_errors += 1
        else:
            return False


    if v4 < 0:
        if v4 >= neg_tolerance:
            acceptable_errors += 1
        else:
            return False

    if v1 == 0 and v2 == 0 and v3 == 0 and v4 ==0:
        return False

    if acceptable_errors <= 2:
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

## Actual Code Begins
## input_file_names contains the names of the json files that we need to analyze
## the files must be in chronological order
## these names are the output files from UIED


input_directory = '../../input/'
input_json_directory = '../../data/output/'
input_ocr_directory = '../../ocr_output/'

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
    fn = input_json_directory + input_filenames_without_extension[i] + '/compo.json'
    input_json_file_names.append(fn)


input_ocr_file_names = []

for i in range(len(input_image_file_names)):
    fn = input_ocr_directory + input_filenames_without_extension[i] + '/' + input_filenames_without_extension[i] + '.json'
    input_ocr_file_names.append(fn)


## the array image_file _data contains the data of all the images
## from json to python data

image_json_file_data=[]

for i in range(len(input_json_file_names)):
    with open(input_json_file_names[i]) as f:
        data = json.load(f)
        image_json_file_data.append(data["compos"])

## this dictionary returns the id of a certain rectangle
rect_to_id = dict()

## this dictionary returns the coordinates of a rectangle given the id
id_to_rect = dict()

## A list containing all the rectangles
## Used later in tree generation
all_rect_list=[]

all_objects = []

## populating the above data structures with data from json files
for i in range(len(image_json_file_data)):
    current_image_data = image_json_file_data[i]

    for rect in current_image_data:
        temp=[rect['column_min'], rect['row_min'], rect['column_max'], rect['row_max'],
             (rect['column_max']-rect['column_min']),(rect['row_max']-rect['row_min'])]

        new = True
        for object in all_objects:
            if(is_same_rectangle(rect, object) == True):
                     new = False
                     break
        if(new == False):
            continue

        temp_str = str(temp)

        rect['coordinates'] = temp
        rect['type'] = 'UIED_output'

        if(temp_str in rect_to_id):
            continue
        else:

            all_rect_list.append(temp)

            index=len(rect_to_id)
            rect_to_id[temp_str]=index

            id_to_rect[index] = temp

            rect['id'] = index
            all_objects.append(rect)




## populating the above data structures with data from ocr data from UIED/EAST
for i in range(len(input_ocr_file_names)):
    with open(input_ocr_file_names[i]) as f:
        data = json.load(f)
        data = data["compos"]

    for rect in data:
        temp=[rect['column_min'], rect['row_min'], rect['column_max'], rect['row_max'],
             (rect['column_max']-rect['column_min']),(rect['row_max']-rect['row_min'])]


        new = True
        for object in all_objects:
            if(is_same_rectangle(rect, object) == True):
                     new = False
                     break
        if(new == False):
            continue

        rect['coordinates'] = temp
        rect['type'] = 'TEXT'

        temp_str = str(temp)

        if(temp_str in rect_to_id):
            continue
        else:

            all_rect_list.append(temp)

            index=len(rect_to_id)
            rect_to_id[temp_str]=index

            id_to_rect[index] = temp
            rect['id'] = index
            all_objects.append(rect)

## Processing Loop
## populating the above data structures with data from opencv based analysis
for i in range(len(input_image_file_names)):

    if(i==0):
        continue

    diff_rects_opencv = get_diff_rects_via_opencv(input_image_file_names[i], input_image_file_names[i-1])

    for diff_rect in diff_rects_opencv:
        if(is_big_rect(diff_rect,dsize)):
            continue

        temp_rect = {}
        temp_rect['column_min'] = diff_rect[0]
        temp_rect['row_min'] = diff_rect[1]
        temp_rect['column_max'] = diff_rect[2]
        temp_rect['row_max'] = diff_rect[3]

        new = True
        for object in all_objects:
            if(is_same_rectangle(temp_rect, object) == True):
                     new = False
                     break
        if(new == False):
            continue

        rect = {}
        rect['coordinates'] = diff_rect
        rect['type'] = 'OpenCV_Output'
        rect['column_min'] = diff_rect[0]
        rect['row_min'] = diff_rect[1]
        rect['column_max'] = diff_rect[2]
        rect['row_max'] = diff_rect[3]


        temp_str = str(diff_rect)

        if(temp_str in rect_to_id):
            continue
        else:
            all_rect_list.append(diff_rect)
            index = len(rect_to_id)
            rect_to_id[temp_str] = index
            id_to_rect[index] = diff_rect
            rect['id'] = index
            all_objects.append(rect)






def addAncestor(child_to_ancestor_map, child, ancestor):
    if child in child_to_ancestor_map.keys():
        ## has other ancestors
        child_to_ancestor_map[child].append(ancestor)
    else:
        ## add first ancestor
        child_to_ancestor_map[child] = [ancestor]


child_to_ancestor = dict()


tree_structure = dict()

for rect1 in all_rect_list:
    for rect2 in all_rect_list:
        if(is_inside(rect2, rect1)):
            index = rect_to_id[str(rect1)]

            addAncestor(child_to_ancestor, rect_to_id[str(rect2)], index)

            if(index in tree_structure):
                ## already has other children
                tree_structure[index].append(rect_to_id[str(rect2)])
            else:
                ## add first children
                tree_structure[index]=[rect_to_id[str(rect2)]]



def getImmediateAncestor(child_to_ancestor_map, child):
    all_ancestors = child_to_ancestor_map[child]

    all_ancestors_areas = []

    for ancestor in all_ancestors:
        rect_of_ancestor = id_to_rect[ancestor]
        all_ancestors_areas.append(rect_of_ancestor[4]*rect_of_ancestor[5])

    sorted_ancestors = [x for _,x in sorted(zip(all_ancestors_areas,all_ancestors))]

    return sorted_ancestors[0]


def GenerateXML(tree, fileName) :
    xml_doc = gfg.Element("Nodes")

    for node in tree.keys():
        root = gfg.Element("root")
        root.text = str(node)
        xml_doc.append(root)


        for child in tree[node]:
            child_node = gfg.SubElement(root, "child")
            child_node.text = str(child)

    temp = gfg.ElementTree(xml_doc)

    with open (fileName, "wb") as files:
        temp.write(files)


def GenerateJSON(tree, fileName):
    with open(fileName, 'w') as outfile:
        json.dump(tree, outfile, indent=4, sort_keys=True)


def removeRepitionsFromForest(forest):

    new_forest = dict()

    for node in forest.keys():
        new_forest[node] = []
        children_of_node = forest[node]
        for child in children_of_node:
            immediate_ancestor = getImmediateAncestor(child_to_ancestor, child)
            if( immediate_ancestor == node):
                new_forest[node].append(child)

    return new_forest



tree_structure = removeRepitionsFromForest(tree_structure)


class NodeOfTree:
    def __init__(self, ID, BoundingRectangle, children):
        self.ID = ID
        self.BoundingRectangle = BoundingRectangle
        self.children = children




def hasChildren(id):

    if id in tree_structure.keys():
        return True
    return False


def generateNode(id):

    if(hasChildren(id)):

        all_children = tree_structure[id]

        children_list = []

        for child in all_children:
            node = generateNode(child)
            children_list.append(node)

            bounding_rect = id_to_rect[id]
        bounding_rect = transformCoordinates(bounding_rect, dsize_cameron)
        bounding_rect = [bounding_rect[0], bounding_rect[1], bounding_rect[4], bounding_rect[5]]

        newNode = dict()

        newNode['ID'] = id

        rect = str(bounding_rect)[1:-1]
        rect = rect.replace(" ", "")
        newNode['BoundingRectangle'] = rect

        newNode['children'] = dict()
        newNode['children']['DetailedEntity'] = children_list

        return newNode

    else:
        bounding_rect = id_to_rect[id]
        bounding_rect = transformCoordinates(bounding_rect, dsize_cameron)
        bounding_rect = [bounding_rect[0], bounding_rect[1], bounding_rect[4], bounding_rect[5]]

        newNode = dict()

        newNode['ID'] = id

        rect = str(bounding_rect)[1:-1]
        rect = rect.replace(" ", "")
        newNode['BoundingRectangle'] = rect

        return newNode



output_folder = '../../opencv_output/'

#GenerateXML(tree_structure, output_folder + "cumulative_dom.xml")

GenerateJSON(tree_structure, output_folder + 'cumulative_dom.json')

## for displaying
GenerateJSON(tree_structure, output_folder + 'nodes_in_trees_1.json')
GenerateJSON(tree_structure, output_folder + 'nodes_in_trees_2.json')
GenerateJSON(tree_structure, output_folder + 'nodes_in_trees_3.json')
##

GenerateJSON(id_to_rect, output_folder + 'id_to_rect.json')

GenerateJSON(rect_to_id, output_folder + 'rect_to_id.json')

GenerateJSON({"compos" : all_objects}, output_folder + 'all_objects.json')

#print(tree_structure)

#output = generateNode(0)

#GenerateJSON(output, output_folder + 'output.json')

#print(output)

#print(child_to_ancestor)




'''xml = dict2xml(output, "DetailedEntity")


f = open("output.xml", "w")
f.write(xml)
f.close()'''

#print(xml)


mydict = {
    'name': 'The Andersson\'s',
    'size': 4,
    'children': {
        'DetailedEntity': [
            {
                'name': 'Tom',
                'sex': 'male',
            },
            {
                'name': 'Betty',
                'sex': 'female',
            }
        ]
    },
}
#print(dict2xml(mydict, 'DetailedEntity'))

print("ending opencv analysis")


## id in black background generation

black_img = cv2.imread('../..' + '/mac_work/gui_update/black.png')

black_img = cv2.resize(black_img, dsize)

for diff_rect in all_rect_list:
    if(is_big_rect(diff_rect,dsize)):
        continue

    cv2.rectangle(black_img,(diff_rect[0],diff_rect[1]),(diff_rect[2],diff_rect[3]),(0,255,0),1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (math.floor((diff_rect[0]+diff_rect[2])/2),math.floor((diff_rect[1]+diff_rect[3])/2))
    #org=(diff_rect[0],diff_rect[1])

    fontScale = 0.33
    color = (255, 255, 255)
    thickness = 1

    image = cv2.putText(black_img, str(rect_to_id[str(diff_rect)]), org, font,
                    fontScale, color, thickness, cv2.LINE_AA)


black_img = cv2.resize(black_img, (1200, 745))

cv2.imwrite(output_folder + "numbered_rects_black.png", black_img)


print(output_folder)
print(input_directory)
print(input_json_directory)


## text in black background generation

black_img_path = '../..' + '/mac_work/gui_update/black.png'
# print(black_img_path)

black_img = cv2.imread(black_img_path)


black_img = cv2.resize(black_img, dsize)

for object in all_objects:

    cv2.rectangle(black_img,(object['column_min'], object['row_min']),(object['column_max'], object['row_max']),(0,255,0),1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (math.floor((object['column_min'] + object['column_max'])/2),math.floor((object['row_min'] + object['row_max'])/2))
    #org=(diff_rect[0],diff_rect[1])

    fontScale = 0.33
    color = (255, 255, 255)
    thickness = 1

    '''image = cv2.putText(black_img, str(object['id']), org, font,
                    fontScale, color, thickness, cv2.LINE_AA)'''

    if(object['type'] == "TEXT"):
        cv2.putText(black_img, object['text'] , org, font,
                        fontScale, color, thickness, cv2.LINE_AA)


black_img = cv2.resize(black_img, (1200, 745))

cv2.imwrite(output_folder + "numbered_rects_black_with_text.png", black_img)
