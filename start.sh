#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
pip install -r requirements.txt

# Start Gunicorn with the configuration file
gunicorn -c gunicorn_config.py app:app 