#!/bin/bash
python3 xml_generator.py
python3 xml_to_dict_converter_runtimeid.py
python3 dom_merger.py
python3 fitts_and_hamming.py
