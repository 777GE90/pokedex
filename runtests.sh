#!/bin/bash

# Get script to exit on first failure
set -e

# First run Flake8 PEP tests then the unit tests
# Flake8 
flake8 --filename="*.py" --exclude="temp_venv/*.py,tests/mock_data.py"
echo "Flake8 exit code = $?"

# Load the unit test environment variables
source environment_variables.testing

# Unittests for our app
python3 -m unittest discover tests
