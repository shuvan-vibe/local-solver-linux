#!/bin/bash
echo "=== Local Turnstile Solver (Linux Stealth Mode) ==="
echo ""

# Install system dependencies required for Xvfb virtual display
echo "Checking system dependencies..."
if ! dpkg -s xvfb > /dev/null 2>&1; then
    echo "Installing Xvfb and display dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq xvfb python3-xlib python3-tk scrot locales > /dev/null 2>&1
    sudo locale-gen en_US.UTF-8 > /dev/null 2>&1
    echo "System dependencies installed!"
else
    echo "System dependencies already installed."
fi

echo ""
echo "Installing/Updating Python packages..."
pip3 install -r requirements.txt -q

echo ""
echo "Starting virtual display (Xvfb) so browser runs invisibly..."
# Kill any existing Xvfb on display :99
pkill -f "Xvfb :99" > /dev/null 2>&1
# Start Xvfb on display :99 with a realistic screen resolution
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
export DISPLAY=:99
export LANG=en_US.UTF-8

echo "Virtual display started on :99"
echo ""
echo "Starting Local Solver API..."
echo "DO NOT close this window. Your bot needs this to solve captchas."
echo "The browser is running INVISIBLY on a virtual screen."
python3 main.py
