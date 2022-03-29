from typing_extensions import runtime
import xml.etree.ElementTree as ET
import json
import os
from cv2 import cv2
import numpy as np

from treelib import Node, Tree

from sklearn import tree
import lxml.etree as etree

id_to_rect = {}
rect_to_id = {}
cumulative_dom = {}
runtimeId_to_id_map = {}

all_objects = []

child_to_parent_map = {}

def GenerateJSON(tree, fileName):
    with open(fileName, 'w') as outfile:
        json.dump(tree, outfile, indent=4, sort_keys=True)


def get_coordinates_from_string(string):

    coords = string.split(',')
    #print(len(coords))
    if len(coords) != 4:
        return []

    rect = []
    
    rect.append(int(coords[0]))
    rect.append(int(coords[1]))
  

    rect.append(int(coords[2]) + int(coords[0]))
    rect.append(int(coords[3]) + int(coords[1]))  


    rect.append(int(coords[2]))
    rect.append(int(coords[3]))  

    return rect


#print(get_coordinates_from_string("1,158,1438,608"))


def walk_tree_recursive(root, current_parent_id, last_node_id):

    if root.tag == 'DetailedEntity' or root.tag == 'children':
        if root.tag == 'DetailedEntity':
            
            id = str(root.attrib['RuntimeId'])   
            rect = get_coordinates_from_string(root.attrib['BoundingRectangle']) 
            acceleratorKey = root.attrib['AcceleratorKey'] 
            accesskey = root.attrib['AccessKey']
            controlType = root.attrib['ControlType']
            runtimeId = root.attrib['RuntimeId']
            name = str(root.attrib["Name"])

            # id = name + '_' + id
             

            if(len(rect) == 6):
                temp = {}

                ## convert runtimeId to id
                if id in runtimeId_to_id_map.keys():
                    assigned_id = runtimeId_to_id_map[id]
                else:
                    next_id = len(runtimeId_to_id_map.keys()) + 1
                    runtimeId_to_id_map[id] = next_id
                    assigned_id = next_id
                

                temp["id"] = int(assigned_id)

                id = str(assigned_id)
            
                id_to_rect[id] = rect
                rect_to_id[str(rect)] = int(id)

                if(last_node_id != -1):
                
                    if str(current_parent_id) in cumulative_dom.keys():
                        cumulative_dom[str(current_parent_id)].append(int(id))

                    else:
                        cumulative_dom[str(current_parent_id)] = [int(id)]  

                last_node_id = int(id)   

               

                temp["column_min"] = rect[0]
                temp["row_min"] = rect[1]
                temp["column_max"] = rect[2]
                temp["row_max"] = rect[3]
                temp["width"] = rect[4]
                temp["height"] = rect[5]

                temp['name'] = name

                temp["coordinates"] = rect
                temp["accessKey"] = accesskey
                temp["acceleratorKey"] = acceleratorKey
                temp['controlType'] = controlType
                temp['runtimeId'] = runtimeId
                temp["type"] = "accessibility_api"

                all_objects.append(temp)

        else:
            current_parent_id = last_node_id   
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    for child in root:
        walk_tree_recursive(child, current_parent_id, last_node_id)



def find_object(id, all_objects):

    for object in all_objects:
        if object['id'] == id:
            return object

    return []     

def remove_unnecessary_panes(cumulative_dom):

    # find if a parent is pane

    lists_to_pop = []
    items_to_pop = []

    roots = cumulative_dom.keys()

    for root in roots:

        root_object = find_object(int(root), all_objects)
        
        if(root_object["controlType"] == "ControlType.Pane"):
            children = cumulative_dom[root]

            if (len(children) == 1):
                ## 
                parent_of_root = child_to_parent_map[int(root)]

                cumulative_dom[str(parent_of_root)].append(children[0])

                child_to_parent_map[int(children[0])] = parent_of_root

                lists_to_pop.append((parent_of_root, int(root)))

                items_to_pop.append(root)

        
    for item in items_to_pop:
        cumulative_dom.pop(item)


    for temp in lists_to_pop:
        cumulative_dom[str(temp[0])].remove(int(temp[1]))   

    


input_directory = '../accessibility_api_files/xmls/'

dom_output_dir = '../accessibility_api_files/doms/'

object_output_dir = '../accessibility_api_files/objects/'

input_xmls = os.listdir(input_directory)

i = 0

print(input_xmls)

for input_xml in input_xmls:

    input_file_name = input_xml

    tree = ET.parse(input_directory + input_file_name)

    root = tree.getroot()

    # print(root.attrib['BoundingRectangle'])

    walk_tree_recursive(root, 1, -1)


    # GenerateJSON(id_to_rect, '../accessibility_api_files/id_to_rect.json')
    # GenerateJSON(rect_to_id, '../accessibility_api_files/rect_to_id.json')


    GenerateJSON({"compos" : all_objects}, object_output_dir + str(i) + '.json')

   


    number_of_shortcuts = 0
    for obj in all_objects:
        if obj["acceleratorKey"] == "" and obj["accessKey"] == "":
            number_of_shortcuts += 1

    # print(len(id_to_rect.keys()))

    # print("number_of_shortcuts : ", len(all_objects) - number_of_shortcuts)

    for root in cumulative_dom.keys():
        children = cumulative_dom[root]

        for child in children:
            child_to_parent_map[int(child)] = int(root)

    for j in range(100):
        remove_unnecessary_panes(cumulative_dom)


    # print(cumulative_dom)


    GenerateJSON(cumulative_dom, dom_output_dir + str(i) + '.json')

    id_to_rect = {}
    rect_to_id = {}
    cumulative_dom = {}

    all_objects = []

    child_to_parent_map = {}

    i += 1


for key in runtimeId_to_id_map.keys():
    print(key, runtimeId_to_id_map[key])