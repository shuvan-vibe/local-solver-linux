#!/bin/bash
echo "=== Local Turnstile Solver (Linux Stealth Mode) ==="
echo ""

# Install system dependencies required for Xvfb virtual display
# (These are the same packages recommended in the Stealthy Playwright video)
echo "Checking system dependencies..."
if ! dpkg -s xvfb > /dev/null 2>&1; then
    echo "Installing Xvfb and display dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq xvfb python3-xlib python3-tk scrot locales > /dev/null 2>&1
    # Set locale (recommended for stealth)
    sudo locale-gen en_US.UTF-8 > /dev/null 2>&1
    echo "System dependencies installed!"
else
    echo "System dependencies already installed."
fi

echo ""
echo "Installing/Updating Python packages..."
pip3 install -r requirements.txt -q

echo ""
echo "Starting Local Solver API..."
echo "DO NOT close this window. Your bot needs this to solve captchas."
export LANG=en_US.UTF-8
python3 main.py
