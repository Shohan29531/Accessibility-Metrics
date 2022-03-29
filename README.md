# GUI Content Detection


## Main
After cloning this repository, the two files of interest are as follows:

> cd mac_works/gui_update \
> python3 Dom_gen.py

This file takes all the ``UIED/EAST/OCR`` output data into consideration and mixes them with opencv based analysis. The output here will be more than one file. All the outputs are inside the ``/opencv_output`` folder.


> cd my_works \
> python3 fitts_and_hamming.py

This file calculates the metrics and finds an ordering of the children for each node. The outputs are also inside the ``/opencv_output`` folder.

To run these two files, please use the **python3** command.


## Visualization
* Run the ``plotly_works/project.py`` file for seeing all the nodes without collapsing, and
* Run the ``plotly_works/project_mod.py`` file for the collapsible version.


## Minimum Requirements/Dependency
Python~=3.5 \
Numpy~=1.15.2 \
Opencv~=3.4.2 \
Tensorflow~=1.1 0.0 \
Keras~=2.2.4 \
Sklearn~=0.22.2 \
Pandas~=0.23.4

## Download Packages:
``pip3 install opencv-python`` \
``pip3 install opencv-contrib-python`` \
``pip3 install treelib`` \
``pip3 install graphviz`` \
``pip3 install sklearn`` \
``pip3 install lxml`` \
``pip3 install pandas`` \
``pip3 install dash`` \
``pip3 install plotly-express`` \
``pip3 install dash_html_components`` \
``pip3 install python-igraph`` \
``pip3 install jupyter-dash -q`` \
``pip3 install dash_cytoscape -q`` \
 ``pip3 install Pillow`` \
 ``pip3 install scikit-image``
