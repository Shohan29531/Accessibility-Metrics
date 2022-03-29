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
import csv

print("fitts and hamming starting")

##### Paramaters for enabling shortcuts

accessibility_api_flag = True
accessibility_api_flag_with_shortcut = False

max_nodes = 1000


## ##### Parameters to use openCV based testing

dsize = (799, 662)

jsonfilepath = '../opencv_output/all_objects.json'
id_to_rect_filepath = '../opencv_output/id_to_rect.json'
rect_to_id_filepath = '../opencv_output/rect_to_id.json'
cumulative_dom_filepath = '../opencv_output/cumulative_dom.json'

output_dir = '../opencv_output/'
output_folder = '../opencv_output/'


with open(jsonfilepath) as f:
    all_objects = json.load(f)
    all_objects = all_objects["compos"]

with open(id_to_rect_filepath) as f:
    id_to_rect = json.load(f)

with open(rect_to_id_filepath) as f:
    rect_to_id = json.load(f)

with open(cumulative_dom_filepath) as f:
    cumulative_dom = json.load(f)

root = 0

tolerance = 5
neg_tolerance = -5


############ change parameters if accessibility flag is used

if accessibility_api_flag:

    jsonfilepath = '../accessibility_api_files/all_objects_final.json'
    id_to_rect_filepath = '../accessibility_api_files/id_to_rect.json'
    rect_to_id_filepath = '../accessibility_api_files/rect_to_id.json'
    cumulative_dom_filepath = '../accessibility_api_files/cumulative_dom_final.json'

    output_dir = '../accessibility_api_files/output/'
    output_folder = '../accessibility_api_files/output/'

    with open(jsonfilepath) as f:
        all_objects = json.load(f)
        all_objects = all_objects["compos"]

    with open(id_to_rect_filepath) as f:
        id_to_rect = json.load(f)

    with open(rect_to_id_filepath) as f:
        rect_to_id = json.load(f)

    with open(cumulative_dom_filepath) as f:
        cumulative_dom = json.load(f)

    root = 1

    dsize = (int(all_objects[0]["width"]), int(all_objects[0]["height"]))  

    print(dsize) 


child_to_parent_map = {}

for key in cumulative_dom:
    children = cumulative_dom[key]

    for child in children:
        child_to_parent_map[child] = int(key)






def find_object(id, all_objects):

    for object in all_objects:
        if object['id'] == id:
            return object

    return []        




def calculate_fitts_metrics( src_id, dest_id, all_objects ):
    src = find_object(src_id, all_objects)
    dest = find_object(dest_id, all_objects)

    dest_area = (dest['column_max'] - dest['column_min']) * (dest['row_max'] - dest['row_min'])

    src_center = ((src['column_max'] + src['column_min'])/2.0, (src['row_max'] + src['row_min'])/2.0)
    dest_center = ((dest['column_max'] + dest['column_min'])/2.0, (dest['row_max'] + dest['row_min'])/2.0)

    distance = math.hypot((src_center[0] - dest_center [0]), (src_center[1] - dest_center [1]))

    output = {}

    output['distance'] = distance
    output['target_area'] = dest_area


    height = 11.766
    width = 20.918

    pixel_length = 11.766/1080
    #pixel_length = 1.0


    output['normalized_distance'] = distance*pixel_length
    output['normalized_dest_area'] = dest_area/(dsize[0] * pixel_length * dsize[1] * pixel_length)

    output['ratio'] = distance/dest_area
    output['normalized_ratio'] =  output['normalized_distance']/output['normalized_dest_area']

    return output





def bubble_sort(children_tuples):

    ## 0- id, 1- col, 2- row

    n = len(children_tuples)

    for i in range(n-1):
        for j in range(0, n-i-1):
            ## compare rows first
            row_diff = children_tuples[j][2] - children_tuples[j + 1][2]

            if row_diff > tolerance:
                children_tuples[j], children_tuples[j + 1] = children_tuples[j + 1], children_tuples[j]

            elif row_diff <= tolerance and row_diff >= neg_tolerance:
                col_diff =  children_tuples[j][1] - children_tuples[j + 1][1]

                if col_diff > 0:
                    children_tuples[j], children_tuples[j + 1] = children_tuples[j + 1], children_tuples[j]

    return children_tuples



def sorting_key(item):
    return (item[2], item[1])



def order_children(parent_id):

    children = cumulative_dom[str(parent_id)]

    children_tuples = []

    for child in children:
        child_object = id_to_rect[str(child)]
        temp = (child, child_object[0], child_object[1])

        children_tuples.append(temp)


    #sorted_children = sorted(children_tuples, key = sorting_key)

    sorted_children = bubble_sort(children_tuples)
    sorted_children_keys = []

    for child in sorted_children:
        sorted_children_keys.append(child[0])

    cumulative_dom[str(parent_id)] = sorted_children_keys


#print(cumulative_dom)

## order the children in cumulative dom only if 
## the dom is created from openCV

if accessibility_api_flag == False:
    for parent in cumulative_dom:
        order_children(int(parent))




def get_path_to_root(id):

    path = [id]

    current = id

    while(True):
        if(current == root):
            break

        if current in child_to_parent_map:
            current = child_to_parent_map[current]
            path.append(current)
        else:
            #print(current)
            return []

    return path




def calculate_hamming_distance( src_id, dest_id, all_objects):

    journey = []

    src = find_object(src_id, all_objects)
    dest = find_object(dest_id, all_objects)

    if src == [] or dest == []:
        return {}

    if accessibility_api_flag and accessibility_api_flag_with_shortcut:
        if dest["accessKey"] != "" or dest["acceleratorKey"] != "":
            ## shortcut exists
            list_accessKey = []
            list_acceleratorKey = []
            if dest["accessKey"] != "":
                list_accessKey = dest["accessKey"].split(",")
            if dest["acceleratorKey"] != "":
                list_acceleratorKey = dest["acceleratorKey"].split("+")

            steps = 1  

            if len(list_accessKey) > len(list_acceleratorKey):   
                steps = len(list_accessKey) - 1
            else:
                steps =  len(list_acceleratorKey) - 1    

            if steps < 1:
                steps = 1    

            #print(steps)    

            journey.append(src_id)
            journey.append(dest_id)    
            output ={}

            output['ups'] = 0
            output['downs'] = 0
            output['left_right'] = 0
                
            output['shortcut'] = steps

            output['total'] = steps
            output['path'] = journey

            return output



    src_path = get_path_to_root(src_id)
    dest_path = get_path_to_root(dest_id)

    if(src_path == [] or dest_path == []):
        if src_path == []: print(src_id)
        if dest_path == []: print(dest_id)
        return {}

    #print(src_path, dest_path)

    len1 = len(src_path)
    len2 = len(dest_path)

    i = len1 - 1
    j = len2 - 1

    ups = 0         #parent
    downs = 0       #child
    left_right = 0  #sibling

    while(True):
        last_src = src_path[i]
        last_dest = dest_path[j]

        if(last_src == last_dest):
            i-=1
            j-=1
        else:
            break

        if(i==-1 or j==-1):
            break

    ## handle complete path overlap cases
    if(i==-1):
        downs = (j+1)

        journey.append(src_path[0])
        current = src_path[0]
        for x in range(j, -1, -1):
            next = dest_path[x]

            children_of_current = cumulative_dom[str(current)]

            index = children_of_current.index(next)

            left_right += index

            for y in range(0, index+1, 1):
                journey.append(children_of_current[y])

            current = next

        output ={}

        output['ups'] = ups
        output['downs'] = downs
        output['left_right'] = left_right
        output['total'] = ups + downs + left_right
        output['path'] = journey

        return output


    elif(j==-1):
        ups = (i+1)
        for x in range(i, -1, -1):
            journey.append(src_path[x])

        output ={}

        output['ups'] = ups
        output['downs'] = downs
        output['left_right'] = left_right
        output['total'] = ups + downs + left_right
        output['path'] = journey
        return output



    ## up movement calculation is simple
    ups = i

    for x in range(i+1):
        journey.append(src_path[x])

    ## calculate path switching costs (left_right only)

    src_node = src_path[i]
    dest_node = dest_path[j]

    imm_parent = child_to_parent_map[src_node]

    siblings = cumulative_dom[str(imm_parent)]

    index1 = siblings.index(src_node)
    index2 = siblings.index(dest_node)

    left_right += abs(index1 - index2)

    ## need to go left
    if(index1 > index2):
        for x in range(index1 - 1, index2, -1):
            journey.append(siblings[x])
    else:
        for x in range(index1 + 1, index2, 1):
            journey.append(siblings[x])




    ## down movement calculation
    ## can be simply down movements or down and left_right

    downs += j

    for k in range(j, 0, -1):

        current = dest_path[k]
        journey.append(current)

        next = dest_path[k-1]

        children_of_current = cumulative_dom[str(current)]

        index = children_of_current.index(next)

        left_right += index

        for x in range(0, index, 1):
            journey.append(children_of_current[x])

    journey.append(dest_path[0])

    output ={}

    output['ups'] = ups
    output['downs'] = downs
    output['left_right'] = left_right
    output['total'] = ups + downs + left_right
    output['path'] = journey


    return output



### method used for allowing mid path shortcuts

def adjust_hamm_with_mid_path_shortcut(old_hamm):

    path = old_hamm["path"]

    src = path[0]
    dest = path[len(path) - 1]

    for i in range(len(path) - 1, -1, -1):

        item = path[i]

        object_item = find_object(item, all_objects)

        if accessibility_api_flag and accessibility_api_flag_with_shortcut:
            if object_item["accessKey"] != "" or object_item["acceleratorKey"] != "":
                ## shortcut exists
                hamm = calculate_hamming_distance(int(item), int(dest), all_objects)

                if hamm == {}:
                    return old_hamm

                list_accessKey = []
                list_acceleratorKey = []
                if object_item["accessKey"] != "":
                    list_accessKey = object_item["accessKey"].split(",")
                if object_item["acceleratorKey"] != "":
                    list_acceleratorKey = object_item["acceleratorKey"].split("+")

                steps = 1  

                if len(list_accessKey) > len(list_acceleratorKey):   
                    steps = len(list_accessKey) - 1
                else:
                    steps =  len(list_acceleratorKey) - 1   

                if steps < 1:
                    steps = 1    

                hamm["shortcut"] = steps
                hamm["total"] = hamm["total"] + steps
                hamm["path"].reverse()
                hamm["path"].append(src)
                hamm["path"].reverse()

                return hamm

    
    return old_hamm




def value_at_percentile(arr, percentile):

    for i in range(0, len(arr)):
        if(arr[i] > percentile):
            return (i, arr[i])




def average(lst):
    return sum(lst) / len(lst)

## Output data generation step


cost_contribution_of_each_node = []
out_cost_contribution_of_each_node = []
appearance_count_of_each_node = []
appearance_count_of_each_node_out = []

for i in range(max_nodes):
    cost_contribution_of_each_node.append(0)
    out_cost_contribution_of_each_node.append(0)

for i in range(max_nodes):
    appearance_count_of_each_node.append(0)
    appearance_count_of_each_node_out.append(0)

header = ['source', 'destination', 'hamming_distance_ups', 'hamming_distance_downs',
 'ups_plus_downs', 'hamming_distance_LR', 'hamming_distance_total',
  'fitts_ratio', 'normalized_fitts_ratio']

file =  open(output_dir + 'pairwise_data_our_exp.csv', 'w', newline ='')

if accessibility_api_flag == True and accessibility_api_flag_with_shortcut == False:
    file =  open(output_dir + 'pairwise_data_GT_no_shortcut.csv', 'w', newline ='')

if accessibility_api_flag == True and accessibility_api_flag_with_shortcut == True:
    file =  open(output_dir + 'pairwise_data_GT_shortcut.csv', 'w', newline ='')

writer = csv.writer(file, delimiter=',')
writer.writerow(i for i in header)

valid_d = 379
nod = 19

p4 = 0.4/(valid_d*nod)
p3 = 0.3/(valid_d*nod)
p2 = 0.2/(valid_d*nod)
p1 = 0.1/(valid_d*nod)

b4 = [21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35, 64, 66, 67, 68, 69, 104, 110]
b3 = [210, 211, 212, 214, 216, 217, 218, 220, 222, 224, 226, 227, 228, 230, 231, 232, 233, 235, 236]
b2 = [259, 262, 263, 266, 267, 268, 269, 272, 273, 274, 275, 276, 279, 280, 281, 282, 285, 286, 287]

b1 = [9, 11, 12, 13, 14, 15, 16, 17, 540, 541, 542, 544, 545, 547, 548, 549, 555, 556, 557]


score = 0

for i in range(len(all_objects)):
    print(i)
    for j in range(len(all_objects)):
        if(i == j):
            continue
        else:
            
            first = all_objects[i]
            second = all_objects[j]


            ## filter the Panes
            if first["controlType"] == "ControlType.Pane" or second["controlType"] == "ControlType.Pane":
                continue

            ## Filter the close, minimize, and maximize button

            if first['name'] == 'Close' or first['name'] == 'Minimize' or first['name'] == 'Maximize':
                continue

            if second['name'] == 'Close' or second['name'] == 'Minimize' or second['name'] == 'Maximize':
                continue


            ## check for non-terminal nodes only

            if str(first["id"]) in cumulative_dom.keys() or str(second["id"]) in cumulative_dom.keys():
                continue

            ## Filter items in status bar

            filter = False

            src_path_to_root = get_path_to_root(first["id"])
            dest_path_to_root = get_path_to_root(second["id"])

            for item in src_path_to_root:
                item_object = find_object(item, all_objects)

                if item_object['name'] == "Status Bar":
                    filter = True
                    break

            for item in dest_path_to_root:
                item_object = find_object(item, all_objects)

                if item_object['name'] == "Status Bar":
                    filter = True
                    break


            if filter == True:
                continue
            

            hamm = calculate_hamming_distance(first["id"], second["id"], all_objects)
                
            if(hamm == {}):
                continue
            else:
                if("shortcut" not in hamm.keys()):
                    hamm = adjust_hamm_with_mid_path_shortcut(hamm)


                if(second["id"] in b4):
                    score += hamm['total'] * p4
                elif(second["id"] in b3):
                    score += hamm['total'] * p3    

                elif(second["id"] in b2):
                    score += hamm['total'] * p2              

                elif(second["id"] in b1):
                    score += hamm['total'] * p1    


                fitts = calculate_fitts_metrics(first["id"], second["id"], all_objects)

                fitts_ratio = fitts['ratio']

                normalized_fitts_ratio = fitts['normalized_ratio']

   
            line = [first["id"], second["id"], hamm['ups'], hamm['downs'], hamm['ups'] + hamm['downs'], hamm['left_right'], hamm['total'], fitts_ratio, normalized_fitts_ratio]

            writer.writerow(line)


file.close()

print(score)









