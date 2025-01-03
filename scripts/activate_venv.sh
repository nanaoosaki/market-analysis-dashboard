# For Unix/Linux/MacOS
#!/bin/bash

if [ ! -d "py310" ]; then
    echo "Creating virtual environment..."
    python -m venv py310
fi

# Activate virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    source py310/bin/activate
    echo "Virtual environment activated"
fi

# Check if requirements are installed
if ! pip freeze | grep -q "yfinance"; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi 