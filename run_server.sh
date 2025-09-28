#!/bin/bash
# This script launches the server from the project root.
# It sets the PYTHONPATH to include the project root, so that the
# 'src' package can be found.
export PYTHONPATH=/app
uvicorn src.main:app --host 0.0.0.0 --port 8000