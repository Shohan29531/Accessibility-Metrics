
#!pip install jupyter-dash -q

from jupyter_dash import JupyterDash

# essential imports
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

import plotly.express as px
import math
from dash import no_update

import pandas as pd
import numpy as np
import json

#!pip install python-igraph

import igraph
from igraph import Graph, EdgeSeq, plot
import plotly.graph_objects as go


rects_with_stages = []

file = open('nodes_in_trees_1.json')
rects_with_stages.append(json.load(file))




file = open('id_to_rect.json')
id_to_rect = json.load(file)


file = open('rect_to_id.json')
rect_to_id = json.load(file)



child_to_parent_map = {}

for key in rects_with_stages[0].keys():
    children = rects_with_stages[0][key]
    
    for child in children:
        child_to_parent_map[child] = int(key)


def get_max_node_id(stage):
  max_node_id = 0

  for key in rects_with_stages[stage].keys():
    if(int(key) > max_node_id):
      max_node_id = int(key)

    children = rects_with_stages[stage][key]

    for child in children:
      if(int(child) > max_node_id):
        max_node_id = int(child)

  return max_node_id

node_show_flags = []

for i in range(get_max_node_id(0) + 1):
    node_show_flags.append(True)

def populate_nodes_and_edges(stage):


  print(node_show_flags)  
  tree_nodes = []
  tree_edges = []

  for key in rects_with_stages[stage].keys(): 

    if int(key) in child_to_parent_map.keys():
        parent = child_to_parent_map[int(key)]

        if node_show_flags[int(parent)] == False:
            continue

    node = {'data': {'label': int(key), 'id': int(key), 'color': 'red'}}
    tree_nodes.append(node)  

    if node_show_flags[int(key)] == False:
        continue  
    children = rects_with_stages[stage][key]
   
    for child in children: 
      node = {'data': {'label': int(child), 'id': int(child), 'color': 'red'}}
      tree_nodes.append(node)    
      edge = {'data': {'source': int(key), 'target': int(child)}}
      tree_edges.append(edge)  

  return tree_nodes, tree_edges




def show_hide_children(parent_id, flag):
    node_show_flags[int(parent_id)] = flag

    print(parent_id, flag)

    all_parents = rects_with_stages[0].keys()

    if parent_id not in all_parents:
        return

    children = rects_with_stages[0][parent_id]
    
    print(children)

    for child in children:
        if str(child) in all_parents:
            show_hide_children(str(child), flag)



#!pip install dash-cytoscape -q

# library of graph
import dash_cytoscape as cyto 
# json parser
import json

from PIL import Image
from skimage import io


# this css creates columns and row layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

## Uncomment the following line for runnning in Google Colab
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

## Uncomment the following line for running in a webbrowser
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def get_rect_coordinates(rect):
  top = rect[0]
  left = rect[1]
  width = rect[4]
  height = rect[5]

  X = [top, top + width, top + width, top, top]
  Y = [left, left, left + height, left + height, left]

  return X, Y



stage = 0

tree_nodes, tree_edges = populate_nodes_and_edges(stage)


img = io.imread('capture_16_resized.png')
fig_img = px.imshow(img, height=827, width=999)


rect = id_to_rect['0']

X, Y = get_rect_coordinates(rect)

fig_img.add_trace(
    go.Scatter(x=X, y=Y)
)





app.layout = html.Div([
                       
    html.H1('Domain Tree Of GUI Objects'),

    html.H6('(click on a node on the tree to see its corresponding rectangle on the right)'),
 
    
    html.Div([
              
      html.H3('Select Stage:'),        
              
      html.Div([
            html.Div(id='empty-div2', children='')
        ],className='two columns'),


      html.Div([
          dcc.Slider(
            id='stage-slider',
            min = 1,
            max = 1,
            value = 1,
            marks={str(x): str(x) for x in [1]},
            step = None
        )
      ], className = 'two columns'),  
      

        

    ], className='row'),



    html.Div([
        html.Div([
            cyto.Cytoscape(
                id='org-chart',
                autoungrabify=True,
                layout={'name': 'breadthfirst'},
                style={'height': '95vh', 'width': '100%'},
                elements = tree_edges + tree_nodes
            )
        ], className='six columns'),


        html.Div([
          dcc.Graph(
              id = 'gui-image',
              figure = fig_img
              ),
        ], className='six columns'),



    ], className='row'),


])


## node information update
## image update with rect marked

@app.callback(
    Output('gui-image', 'figure'),
    Output('org-chart','elements'),
    Input('org-chart','tapNodeData')
)

def update_nodes(data):
  if data is None:
    return no_update
  else:  
    id = data['id']
    rect = id_to_rect[id]
    
    fig_img = px.imshow(img, height=827, width=999)

    X, Y = get_rect_coordinates(rect)

    fig_img.add_trace(
        go.Scatter(x=X, y=Y)
    )

    if node_show_flags[int(id)] == True:
        show_hide_children(id, False)
    else:
        show_hide_children(id, True)   





    
    tree_nodes, tree_edges = populate_nodes_and_edges(0)
    elements = tree_edges + tree_nodes
    
    
    return fig_img, elements


    
    

# end update

## uncomment this line for running in Google Colab
#app.run_server(mode='inline', port=8040)

## uncomment the following lines for running in dash
if __name__ == '__main__':
  app.run_server(debug=True)