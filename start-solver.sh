#!/bin/bash
echo "Installing/Updating required packages..."
pip3 install -r requirements.txt

echo "Starting Local Solver API..."
echo "DO NOT close this window. Your bot needs this to solve captchas."
python3 main.py
