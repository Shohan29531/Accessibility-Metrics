import xml.etree.ElementTree as ET
from cv2 import cv2
import numpy as np
from treelib import Node, Tree

from sklearn import tree
import lxml.etree as etree


def write_xml(all_lines, filename):
    file = open(filename, 'w')

    for i in range(1, len(all_lines)):
        file.write(all_lines[i] + "\n")

    file.close() 



file = open('../accessibility_api_files/word.log', encoding="utf8", errors='ignore')

lines = file.read().splitlines()
file.close()



all_xmls = []
current_xml = []

count = 0
i = 0
for line in lines:

    line_stripped = line.lstrip()

    if line == "":
        continue

    if line_stripped[0] == '<':
        current_xml.append(line)

    else:
        all_xmls.append(current_xml)
        
        if len(current_xml) >= 1:

            count += 1

            filename = '../accessibility_api_files/xmls/' + str(i) + '.xml'

            write_xml(current_xml, filename)
            i += 1  

        current_xml = []

      

print(count)
