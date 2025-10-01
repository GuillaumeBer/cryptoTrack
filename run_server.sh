#!/bin/bash
# This script launches the server from the project root.
# It sets the PYTHONPATH to include the project root, so that the
# 'src' package can be found.
export PYTHONPATH=/app
python run.py