
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


file = open('nodes_in_trees_1.json')
rects_with_stages.append(json.load(file))


file = open('nodes_in_trees_1.json')
rects_with_stages.append(json.load(file))


file = open('all_objects.json')
all_objects = json.load(file)

all_objects = all_objects["compos"]

file = open('id_to_rect.json')
id_to_rect = json.load(file)


file = open('rect_to_id.json')
rect_to_id = json.load(file)

id_to_text = {}

for compo in all_objects:
  if(compo["type"] == "TEXT"):
    id_to_text[compo["id"]] = compo["text"]
  else:
    id_to_text[compo["id"]] = "###"
  


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



def populate_nodes_and_edges(stage):
  tree_nodes = []
  tree_edges = []

  max_node_id = get_max_node_id(stage)

  for i in range(max_node_id+1):
    node = {'data': {'label': str(i) + ": " + str(id_to_text[i]), 'id': i, 'color': 'red'}}
    tree_nodes.append(node)

  for key in rects_with_stages[stage].keys():
    children = rects_with_stages[stage][key]
   
    for child in children: 
      edge = {'data': {'source': int(key), 'target': int(child)}}
      tree_edges.append(edge)  

  return tree_nodes, tree_edges

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
            max = 3,
            value = 1,
            marks={str(x): str(x) for x in [1, 2, 3]},
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
                elements= tree_edges + tree_nodes
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

## graph update stage

@app.callback(
    Output('org-chart','elements'),
    Input('stage-slider','value')
)


def update_graph_stage(data):

  stage = data -1
  tree_nodes, tree_edges = populate_nodes_and_edges(stage)
  elements = tree_edges + tree_nodes
  return elements


## node information update
## image update with rect marked

@app.callback(
    Output('gui-image', 'figure'),
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
    
    return fig_img


    
    

# end update

## uncomment this line for running in Google Colab
#app.run_server(mode='inline', port=8040)

## uncomment the following lines for running in dash
if __name__ == '__main__':
  app.run_server(debug=True)
