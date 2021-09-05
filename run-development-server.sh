#!/bin/bash

python3 -m venv temp_venv
source temp_venv/bin/activate

pip3 install --upgrade pip
pip3 install -r requirements.txt

source environment_variables

python3 server.py
