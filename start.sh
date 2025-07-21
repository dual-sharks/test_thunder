#!/bin/bash

# Start Jupyter notebook in the background
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &

# Start Flask API
python app.py
