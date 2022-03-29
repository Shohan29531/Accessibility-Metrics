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


print("dom merger starting")

jsonfilepath = '../accessibility_api_files/all_objects_old.json'
id_to_rect_filepath = '../accessibility_api_files/id_to_rect.json'
rect_to_id_filepath = '../accessibility_api_files/rect_to_id.json'
cumulative_dom_filepath = '../accessibility_api_files/cumulative_dom_old.json'

output_dir = '../accessibility_api_files/output/'
output_folder = '../accessibility_api_files/output/'

with open(jsonfilepath) as f:
    # all_objects = json.load(f)
    # all_objects = all_objects["compos"]
    all_objects = []

with open(id_to_rect_filepath) as f:
     id_to_rect = json.load(f)

with open(rect_to_id_filepath) as f:
    rect_to_id = json.load(f)

with open(cumulative_dom_filepath) as f:
    # cumulative_dom = json.load(f)
    cumulative_dom = {}


existing_ids = []

for item in all_objects:
    existing_ids.append(item["id"])


def GenerateJSON(tree, fileName):
    with open(fileName, 'w') as outfile:
        json.dump(tree, outfile, indent=4, sort_keys=True)





def merge_doms (new_dom_path):

    with open(new_dom_path) as f:
        new_dom = json.load(f)  

    parents1 = list(cumulative_dom.keys())
    parents2 = list(new_dom.keys())

    parents = parents1 + parents2

    parents = list(set(parents))

    for parent in parents:

        if parent in parents1 and parent in parents2:
            ## most probably identical children list

            children_list1 = cumulative_dom[parent]
            children_list2 = new_dom[parent]

            if set(children_list1) == set(children_list2):
                my = 0
                # print(set(children_list1))
            else:
                # print("Exception Found")    
                # print(children_list1, children_list2)

                new_children_list = children_list1 + children_list2
                new_children_list = list(set(new_children_list))
                cumulative_dom[parent] = new_children_list

        elif parent not in parents1 and parent in parents2:
            children_list2 = new_dom[parent]

            cumulative_dom[parent] = children_list2
    
   

       
def merge_objects(new_objects_path):
    with open(new_objects_path) as f:
        new_objects = json.load(f)
        new_objects = new_objects["compos"]    

    for new_object in new_objects:
        if new_object["id"] not in existing_ids:
            existing_ids.append(new_object["id"])

            all_objects.append(new_object)


   




input_dom_directory = '../accessibility_api_files/doms/'
input_object_directory = '../accessibility_api_files/objects/'


input_doms = os.listdir(input_dom_directory)
input_objects = os.listdir(input_object_directory)


for i in range(len(input_doms)):

    new_dom = input_doms[i]
    new_objects = input_objects[i]
  
    merge_doms(input_dom_directory + new_dom)
    merge_objects(input_object_directory + new_objects)





GenerateJSON(cumulative_dom, '../accessibility_api_files/cumulative_dom_final.json') 

GenerateJSON({"compos" : all_objects}, '../accessibility_api_files/all_objects_final.json')