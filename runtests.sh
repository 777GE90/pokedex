#!/bin/sh

# Get script to exit on first failure
set -e

# First run Flake8 PEP tests then the unit tests
# Flake8 
flake8 --filename="*.py" --exclude="temp_venv/*.py"
echo "Flake8 exit code = $?"

# Unittests for our app
python3 -m unittest discover tests
