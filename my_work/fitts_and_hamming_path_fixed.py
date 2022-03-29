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

dsize = (799, 662)

jsonfilepath = '../opencv_output/all_objects.json'
id_to_rect_filepath = '../opencv_output/id_to_rect.json'
rect_to_id_filepath = '../opencv_output/rect_to_id.json'
cumulative_dom_filepath = '../opencv_output/cumulative_dom.json'

output_dir = '../opencv_output/'

root = 0

tolerance = 5
neg_tolerance = -5

with open(jsonfilepath) as f:
    all_objects = json.load(f)
    all_objects = all_objects["compos"]

with open(id_to_rect_filepath) as f:
    id_to_rect = json.load(f)

with open(rect_to_id_filepath) as f:
    rect_to_id = json.load(f)

with open(cumulative_dom_filepath) as f:
    cumulative_dom = json.load(f)


child_to_parent_map = {}

for key in cumulative_dom:
    children = cumulative_dom[key]

    for child in children:
        child_to_parent_map[child] = int(key)
    

#print(child_to_parent_map)




def find_object(id, all_objects):

    for object in all_objects:
        if object['id'] == id:
            return object




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

## order the children in cumulative dom

for parent in cumulative_dom:
    order_children(int(parent))


#print(cumulative_dom)
#print(child_to_parent_map)

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
            return []    
        
    return path   


def calculate_hamming_distance( src_id, dest_id, all_objects):

    journey = []

    src = find_object(src_id, all_objects)
    dest = find_object(dest_id, all_objects)

    src_path = get_path_to_root(src_id)
    dest_path = get_path_to_root(dest_id)

    if(src_path == [] or dest_path == []):
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

    

    


x= 40
y= 23

#print(cumulative_dom)

with open('new_dom.json', 'w') as outfile:
    json.dump(cumulative_dom, outfile, indent=4, sort_keys=True) 

output = calculate_hamming_distance(x, y, all_objects)

print(output)


print(calculate_fitts_metrics(x, y, all_objects))

#print(id_to_rect["0"], id_to_rect["1"])

    


header = ['source', 'destination', 'hamming_distance_ups', 'hamming_distance_downs', 'hamming_distance_LR', 'hamming_distance_total', 'fitts_ratio', 'normalized_fitts_ratio']

file =  open(output_dir + 'data_2.csv', 'w', newline ='')
writer = csv.writer(file, delimiter=',')
writer.writerow(i for i in header)

 
for i in range(len(all_objects)):
    for j in range(len(all_objects)):
        if(i==j):
            continue
        else:
            hamm = calculate_hamming_distance(i, j, all_objects)
            if(hamm == {}):
                continue
            else:
                #hamm = hamm['total']
                fitts = calculate_fitts_metrics(i, j, all_objects)

                fitts_ratio = fitts['ratio']

                normalized_fitts_ratio = fitts['normalized_ratio'] 

            #print(i, j, end=' ')
            #print(hamm, fitts)

            line = [i, j, hamm['ups'], hamm['downs'], hamm['left_right'], hamm['total'], fitts_ratio, normalized_fitts_ratio]

            writer.writerow(line)


file.close()


#print(cumulative_dom)



black_img = cv2.imread('..' + '/mac works/GUI Update/black.png')

black_img = cv2.resize(black_img, dsize)

for key in cumulative_dom.keys():

    children = cumulative_dom[str(key)]
    
    i = 1
    for child in children:
        current_rect = id_to_rect[str(child)]


        cv2.rectangle(black_img,(current_rect[0],current_rect[1]),(current_rect[2],current_rect[3]),(0,255,0),1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (math.floor((current_rect[0]+current_rect[2])/2),math.floor((current_rect[1]+current_rect[3])/2))
        #org=(diff_rect[0],diff_rect[1])

        fontScale = 0.30
        color = (255, 255, 255)
        thickness = 1

        image = cv2.putText(black_img, str(i), org, font, 
                        fontScale, color, thickness, cv2.LINE_AA) 

        i += 1                   


black_img = cv2.resize(black_img, (1200, 993))

output_folder = '../opencv_output/'

cv2.imwrite(output_folder + "ordered_rects.png", black_img)