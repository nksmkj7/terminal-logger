#!/bin/bash

# Setup script for terminal-logger
echo "Setting up virtual environment for terminal-logger..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if venv module is available
python3 -c "import venv" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Python venv module is not available. Please install it and try again."
    echo "On Debian/Ubuntu: sudo apt-get install python3-venv"
    echo "On CentOS/RHEL: sudo yum install python3-venv"
    echo "On macOS: Python 3 should already include venv"
    exit 1
fi

# Check if virtual environment already exists
if [ -d "venv" ]; then
    read -p "Virtual environment already exists. Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
        source venv/bin/activate
        pip install -r requirements.txt
        echo "Dependencies installed. Activate the virtual environment with:"
        echo "source venv/bin/activate"
        exit 0
    fi
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x terminal_logger.py query_history.py

echo
echo "Setup complete! Virtual environment has been created and activated."
echo
echo "To use terminal-logger, make sure the virtual environment is activated:"
echo "source venv/bin/activate"
echo
echo "To deactivate the virtual environment when done:"
echo "deactivate"
