import json
import os
from cv2 import cv2
import numpy as np
import math
from treelib import Node, Tree

from sklearn import tree
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




def calculate_fitts_metrics_old( src_id, dest_id, all_objects ):
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
    output['normalized_ratio'] =  output['normalized_distance']*2/output['normalized_dest_area']

    if(output['normalized_ratio'] != 0):
        output['log2ratio'] = math.log(output['normalized_ratio'], 2)
    else:
        output['log2ratio'] = 0    

    return output




def calculate_fitts_metrics( src_id, dest_id, all_objects ):
    src = find_object(src_id, all_objects)
    dest = find_object(dest_id, all_objects)

    src_center = ((src['column_max'] + src['column_min'])/2.0, (src['row_max'] + src['row_min'])/2.0)
    dest_center = ((dest['column_max'] + dest['column_min'])/2.0, (dest['row_max'] + dest['row_min'])/2.0)

    output = {}

    output['distance'] = math.hypot((src_center[0] - dest_center [0]), (src_center[1] - dest_center [1]))

    output['target_width_col'] = abs(dest['column_max'] - dest['column_min'])
    output['target_width_row'] = abs(dest['row_max'] - dest['row_min'])

    if output['target_width_row'] < output['target_width_col']:
        output['target_width'] = output['target_width_row']
    else:
        output['target_width'] = output['target_width_col']    

    height = 11.766
    width = 20.918

    pixel_length = 11.766/1080
    #pixel_length = 1.0


    output['normalized_distance'] =  output['distance']*pixel_length
    output['normalized_target_width'] = output['target_width']*pixel_length

    # output['normalized_ratio'] =  2 * output['distance']/output['target_width']

    output['normalized_ratio'] =  output['distance']/output['target_width'] + 1

    # output['log2ratio'] = math.log(output['normalized_ratio'], 2)

    # if(output['normalized_ratio'] !=0 and output['normalized_ratio'] < 1 ):
    #         print(src, dest, output['normalized_ratio'])  

    if(output['normalized_ratio'] != 0):
        output['log2ratio'] = math.log(output['normalized_ratio'], 2)  
    else:
        output['log2ratio'] = 0    

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

header = ['source', 'destination', 'hamming_distance','fitts_ratio']

file =  open(output_dir + 'pairwise_data_our_exp.csv', 'w', newline ='')

if accessibility_api_flag == True and accessibility_api_flag_with_shortcut == False:
    file =  open(output_dir + 'pairwise_data_GT_no_shortcut.csv', 'w', newline ='')

if accessibility_api_flag == True and accessibility_api_flag_with_shortcut == True:
    file =  open(output_dir + 'fitts_v_hamming.csv', 'w', newline ='')

writer = csv.writer(file, delimiter=',')
writer.writerow(i for i in header)

counter = []
for i in range(max_nodes):
    counter.append(0)

count_dict = {}

count_dict["ups"] = []
count_dict["downs"] = []
count_dict["level"] = []
count_dict["ups_plus_downs"] = []
count_dict["total"] = []

count_dict["ups_cum"] = []
count_dict["downs_cum"] = []
count_dict["level_cum"] = []
count_dict["ups_plus_downs_cum"] = []
count_dict["total_cum"] = []


for i in range(max_nodes):
    count_dict["ups"].append(0)
    count_dict["downs"].append(0)
    count_dict["level"].append(0)
    count_dict["ups_plus_downs"].append(0)
    count_dict["total"].append(0)

    count_dict["ups_cum"].append(0)
    count_dict["downs_cum"].append(0)
    count_dict["level_cum"].append(0)
    count_dict["ups_plus_downs_cum"].append(0)
    count_dict["total_cum"].append(0)


for i in range(len(all_objects)):
    print(i)
    for j in range(len(all_objects)):
        if(i == j):
            continue
        else:
            
            first = all_objects[i]
            second = all_objects[j]

            ## for excel (one cell) only
            # if((first["id"] >= 138 and first["id"] <= 390) or (second["id"] >= 138 and second["id"] <= 390)):
            #     continue


            ## filter the Panes
            if first["controlType"] == "ControlType.Pane" or second["controlType"] == "ControlType.Pane":
                continue

            ## Filter the close, minimize, and maximize button

            if first['name'] == 'Close' or first['name'] == 'Minimize' or first['name'] == 'Maximize':
                continue

            if second['name'] == 'Close' or second['name'] == 'Minimize' or second['name'] == 'Maximize':
                continue



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
            
            # for excel only
            # if((first["id"] < 139 or first["id"] > 390) and (second["id"] < 139 or second["id"] > 390)):

            hamm = calculate_hamming_distance(first["id"], second["id"], all_objects)
                
            if(hamm == {}):
                continue
            else:
                if("shortcut" not in hamm.keys()):
                    hamm = adjust_hamm_with_mid_path_shortcut(hamm)

    
                ## Valid only for Calculator application

                # if((first["id"] >= 10 and first["id"] <= 37) or (second["id"] >= 10 and second["id"] <= 37)):
                #     hamm = {}
                #     hamm['ups'] = 0
                #     hamm['downs'] = 0
                #     hamm['left_right'] = 0
                #     hamm['shortcut'] = 1
                #     hamm['total'] = 1


                # ## (START) valid only for excel (A-T, 1-11, ids 139-390)
                
                # if((first["id"] >= 139 and first["id"] <= 390) or (second["id"] >= 139 and second["id"] <= 390)):

                #     if((first["id"] >= 139 and first["id"] <= 390) and (second["id"] >= 139 and second["id"] <= 390)):

                #         my_start = first["id"]
                #         my_end = second["id"]

                #         my_start -= 138
                #         my_end -= 138

                #         row1 = int(my_start/21)
                #         col1 = my_start % 21

                #         row2 = int(my_end/21)
                #         col2 = my_end % 21

                #         tot = abs(row1 - row2) + abs(col1 - col2)

                #         hamm = {}
                #         hamm['ups'] = 0
                #         hamm['downs'] = 0
                #         hamm['left_right'] = 0
                #         hamm['shortcut'] = 0
                #         hamm['total'] = tot

                #     elif((first["id"] >= 139 and first["id"] <= 390) and (second["id"] < 139 or second["id"] > 390)):

                #         hamm = calculate_hamming_distance(139, second["id"], all_objects)

                #         my_start = 139
                #         my_end = first["id"]

                #         my_start -= 138
                #         my_end -= 138

                #         row1 = int(my_start/21)
                #         col1 = my_start % 21

                #         row2 = int(my_end/21)
                #         col2 = my_end % 21

                #         tot = abs(row1 - row2) + abs(col1 - col2)

                #         hamm['total'] = hamm['total'] + tot



                #     elif((first["id"] < 139 or first["id"] > 390) and (second["id"] >= 139 and second["id"] <= 390)):

                #         hamm = calculate_hamming_distance(first["id"], 139, all_objects)

                #         my_start = 139
                #         my_end = second["id"]

                #         my_start -= 138
                #         my_end -= 138

                #         row1 = int(my_start/21)
                #         col1 = my_start % 21

                #         row2 = int(my_end/21)
                #         col2 = my_end % 21

                #         tot = abs(row1 - row2) + abs(col1 - col2)

                #         hamm['total'] = hamm['total'] + tot

                # ## (END) valid only for excel (A-T, 1-11, ids 139-390)

                counter[hamm['total']] += 1

                cost_contribution_of_each_node[int(second["id"])] += hamm['total']
                out_cost_contribution_of_each_node[int(first["id"])] += hamm['total']
                appearance_count_of_each_node[int(second["id"])] += 1
                appearance_count_of_each_node_out[int(first["id"])] += 1

                count_dict["ups"][hamm["ups"]] += 1
                count_dict["downs"][hamm["downs"]] += 1
                count_dict["level"][hamm["left_right"]] += 1
                count_dict["ups_plus_downs"][hamm["ups"] + hamm["downs"]] += 1
                count_dict["total"][hamm['total']] += 1

                fitts = calculate_fitts_metrics(first["id"], second["id"], all_objects)

                # fitts_ratio = fitts['ratio']

                # normalized_fitts_ratio = fitts['normalized_ratio']

                log2_fitts_ratio = fitts['log2ratio']

   
            line = [first["id"], second["id"], hamm['total'], log2_fitts_ratio]

            writer.writerow(line)


file.close()



for i in range(max_nodes):
    if appearance_count_of_each_node[i] != 0:
        cost_contribution_of_each_node[i] = cost_contribution_of_each_node[i] / appearance_count_of_each_node[i]
        

for i in range(max_nodes):
    if appearance_count_of_each_node_out[i] != 0:
        out_cost_contribution_of_each_node[i] = out_cost_contribution_of_each_node[i] / appearance_count_of_each_node_out[i]


## count dict analysis

up_sum = sum(count_dict["ups"])
down_sum = sum(count_dict["downs"])
level_sum = sum(count_dict["level"])
ups_plus_downs_sum = sum(count_dict["ups_plus_downs"])
total_sum = sum(count_dict["total"])


## update with percentiles 
for i in range(max_nodes):
    count_dict["ups"][i] /= up_sum
    count_dict["downs"][i] /= down_sum
    count_dict["level"][i] /= level_sum
    count_dict["ups_plus_downs"][i] /= ups_plus_downs_sum
    count_dict["total"][i] /= total_sum

    
count_dict["ups_cum"][0] = count_dict["ups"][0]
count_dict["downs_cum"][0] = count_dict["downs"][0]
count_dict["level_cum"][0] = count_dict["level"][0]
count_dict["ups_plus_downs_cum"][0] = count_dict["ups_plus_downs"][0]
count_dict["total_cum"][0] = count_dict["total"][0]


for i in range(1, max_nodes):
    count_dict["ups_cum"][i] = count_dict["ups"][i] + count_dict["ups_cum"][i - 1]
    count_dict["downs_cum"][i] = count_dict["downs"][i] + count_dict["downs_cum"][i - 1]
    count_dict["level_cum"][i] = count_dict["level"][i] + count_dict["level_cum"][i - 1]
    count_dict["ups_plus_downs_cum"][i] = count_dict["ups_plus_downs"][i] + count_dict["ups_plus_downs_cum"][i - 1] 
    count_dict["total_cum"][i] = count_dict["total"][i] + count_dict["total_cum"][i - 1] 



#print(count_dict)

expected = {}
expected["ups"] = 0
expected["downs"] = 0
expected["level"] = 0
expected["ups_plus_downs"] = 0
expected["total"] = 0

for i in range(max_nodes):
    expected["ups"] += i * count_dict["ups"][i] 
    expected["downs"] += i * count_dict["downs"][i] 
    expected["level"] += i * count_dict["level"][i]
    expected["ups_plus_downs"] += i * count_dict["ups_plus_downs"][i]  
    expected["total"] += i * count_dict["total"][i]


# print("Expected Moves: \n",expected)


ups_1 = count_dict["ups_cum"][1]
ups_2 = count_dict["ups_cum"][2]
ups_3 = count_dict["ups_cum"][3]
ups_4 = count_dict["ups_cum"][4]
ups_5 = count_dict["ups_cum"][5]

ups_95p = value_at_percentile(count_dict["ups_cum"], 0.95)
ups_99p = value_at_percentile(count_dict["ups_cum"], 0.99)

# print(ups_1, ups_5, ups_95p, ups_99p)



downs_1 = count_dict["downs_cum"][1]
downs_2 = count_dict["downs_cum"][2]
downs_3 = count_dict["downs_cum"][3]
downs_4 = count_dict["downs_cum"][4]
downs_5 = count_dict["downs_cum"][5]

downs_95p = value_at_percentile(count_dict["downs_cum"], 0.95)
downs_99p = value_at_percentile(count_dict["downs_cum"], 0.99)

# print(downs_1, downs_5, downs_95p, downs_99p)



level_1 = count_dict["level_cum"][1]
level_2 = count_dict["level_cum"][2]
level_3 = count_dict["level_cum"][3]
level_4 = count_dict["level_cum"][4]
level_5 = count_dict["level_cum"][5]

level_95p = value_at_percentile(count_dict["level_cum"], 0.95)
level_99p = value_at_percentile(count_dict["level_cum"], 0.99)

# print(level_1, level_5, level_95p, level_99p)




ups_plus_downs_1 = count_dict["ups_plus_downs_cum"][1]
ups_plus_downs_2 = count_dict["ups_plus_downs_cum"][2]
ups_plus_downs_3 = count_dict["ups_plus_downs_cum"][3]
ups_plus_downs_4 = count_dict["ups_plus_downs_cum"][4]
ups_plus_downs_5 = count_dict["ups_plus_downs_cum"][5]

ups_plus_downs_95p = value_at_percentile(count_dict["ups_plus_downs_cum"], 0.95)
ups_plus_downs_99p = value_at_percentile(count_dict["ups_plus_downs_cum"], 0.99)

# print(ups_plus_downs_1, ups_plus_downs_5, ups_plus_downs_95p, ups_plus_downs_99p)


total_1 = count_dict["total_cum"][1]
total_2 = count_dict["total_cum"][2]
total_3 = count_dict["total_cum"][3]
total_4 = count_dict["total_cum"][4]
total_5 = count_dict["total_cum"][5]

total_95p = value_at_percentile(count_dict["total_cum"], 0.95)
total_99p = value_at_percentile(count_dict["total_cum"], 0.99)






print("Shortcut Flag: ", accessibility_api_flag_with_shortcut)

print("\n")

print("Up Move Summary: \n")

print("Percentile at 1 move: ", ups_1)
print("Percentile at 2 moves: ", ups_2)
print("Percentile at 3 moves: ", ups_3)
print("Percentile at 4 moves: ", ups_4)
print("Percentile at 5 moves: ", ups_5)
print("Hamm score at 95th percentile: ",ups_95p)
print("Hamm score at 99th percentile: ", ups_99p)
print("Expteced up moves: ", expected['ups'])

print("\n\n")


print("Down Move Summary: \n")

print("Percentile at 1 move: ", downs_1)
print("Percentile at 2 moves: ", downs_2)
print("Percentile at 3 moves: ", downs_3)
print("Percentile at 4 moves: ", downs_4)
print("Percentile at 5 moves: ", downs_5)
print("Hamm score at 95th percentile: ", downs_95p)
print("Hamm score at 99th percentile: ", downs_99p)
print("Expteced down moves: ", expected['downs'])

print("\n\n")


print("Level Move Summary: \n")

print("Percentile at 1 move: ", level_1)
print("Percentile at 2 move: ", level_2)
print("Percentile at 3 move: ", level_3)
print("Percentile at 4 move: ", level_4)
print("Percentile at 5 moves: ", level_5)
print("Hamm score at 95th percentile: ", level_95p)
print("Hamm score at 99th percentile: ", level_99p)
print("Expteced level moves: ", expected['level'])

print("\n\n")


print("Ups_plus_downs Move Summary: \n")

print("Percentile at 1 move: ", ups_plus_downs_1)
print("Percentile at 2 move: ", ups_plus_downs_2)
print("Percentile at 3 move: ", ups_plus_downs_3)
print("Percentile at 4 move: ", ups_plus_downs_4)
print("Percentile at 5 moves: ", ups_plus_downs_5)
print("Hamm score at 95th percentile: ", ups_plus_downs_95p)
print("Hamm score at 99th percentile: ", ups_plus_downs_99p)
print("Expteced Ups_plus_downs moves: ", expected['ups_plus_downs'])

print("\n\n")


print("Total Move Summary: \n")

print("Percentile at 1 move: ", total_1)
print("Percentile at 2 move: ", total_2)
print("Percentile at 3 move: ", total_3)
print("Percentile at 4 move: ", total_4)
print("Percentile at 5 moves: ", total_5)

print("Hamm score at 10th percentile: ", value_at_percentile(count_dict["total_cum"], 0.10))
print("Hamm score at 20th percentile: ", value_at_percentile(count_dict["total_cum"], 0.20))
print("Hamm score at 50th percentile: ", value_at_percentile(count_dict["total_cum"], 0.50))


print("Hamm score at 80th percentile: ", value_at_percentile(count_dict["total_cum"], 0.80))
print("Hamm score at 95th percentile: ", total_95p)
print("Hamm score at 99th percentile: ", total_99p)

print("Expteced total moves: ", expected['total'])

print("\n\n")


with open(output_folder + 'ordered_dom.json', 'w') as outfile:
        json.dump(cumulative_dom, outfile, indent=4, sort_keys=True)




file2 =  open(output_dir + 'counter.csv', 'w', newline ='')

writer2 = csv.writer(file2, delimiter=',')

writer2.writerow(["number", "count"])

for i in range(len(counter)):

    if(counter[i] != 0):
       
        line = [i, counter[i]]
        writer2.writerow(line)


file2.close()


valid_destinations_count = 0

valid_nodes = []
valid_costs = []

file3 =  open(output_dir + 'contribution.csv', 'w', newline ='')

writer3 = csv.writer(file3, delimiter=',')

writer3.writerow(["dest", "avg_cost_in", "avg_cost_out"])

for i in range(len(cost_contribution_of_each_node)):

    if cost_contribution_of_each_node[i] != 0:  

        line = [i, cost_contribution_of_each_node[i], out_cost_contribution_of_each_node[i]]
        valid_destinations_count += 1
        writer3.writerow(line)
        valid_costs.append(cost_contribution_of_each_node[i])
        valid_nodes.append(i)

file3.close()

print("Total Nodes: ", len(all_objects))
print("Valid Destinations: ", valid_destinations_count)




import glob
import os

xml_path = '../accessibility_api_files/xmls/*'
object_path = '../accessibility_api_files/objects/*'
dom_path = '../accessibility_api_files/doms/*'


files = glob.glob(xml_path)
for f in files:
    os.remove(f)


files = glob.glob(object_path)
for f in files:
    os.remove(f)

files = glob.glob(dom_path)
for f in files:
    os.remove(f)        





import numpy as np

sd = np.std(valid_costs)
mean = average(valid_costs)


sigmia_sumtuplier = 2.5

culprit_nodes = []
good_node_costs = []

print("\nCulprit Nodes: \n")

for i in range(0, len(valid_costs)):
    cost = valid_costs[i]
    val = abs( cost - mean )

    if val >= sigmia_sumtuplier * sd:
        culprit_nodes.append(valid_nodes[i])
        print(valid_nodes[i])

    else:
        good_node_costs.append(valid_costs[i])


print("Multiplier of Sigma: ", sigmia_sumtuplier)
print("Expected moves after removing culprits: ", average(good_node_costs))


sigmia_sumtuplier = 3

culprit_nodes = []
good_node_costs = []

print("Culprit Nodes: \n")

for i in range(0, len(valid_costs)):
    cost = valid_costs[i]
    val = abs( cost - mean )

    if val >= sigmia_sumtuplier * sd:
        culprit_nodes.append(valid_nodes[i])
        print(valid_nodes[i])

    else:
        good_node_costs.append(valid_costs[i])


print("Multiplier of Sigma: ", sigmia_sumtuplier)
print("Expected moves after removing culprits: ", average(good_node_costs))