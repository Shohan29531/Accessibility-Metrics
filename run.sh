#!/bin/bash
conda activate uied_env
python3 run_single.py
conda deactivate
cd my_work
python3 sub_image_extractor.py
python3 cursor_detection.py
cd ..
cd mac_work
cd gui_update
python3 Dom_Gen.py
cd ..
cd ..
