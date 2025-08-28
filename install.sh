#!/bin/bash

# cryoDL Installation Script
# This script installs cryoDL and sets up the CLI command

set -e  # Exit on any error

echo "=== cryoDL Installation Script ==="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $python_version is installed, but Python $required_version or higher is required"
    exit 1
fi

echo "✓ Python $python_version detected"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed or not in PATH"
    echo "Please install pip3 and try again"
    exit 1
fi

echo "pip3 detected"

# Install the package
echo
echo "Installing cryoDL..."
pip3 install -e .

# Verify installation
if command -v cryodl &> /dev/null; then
    echo "✓ cryoDL CLI installed successfully!"
    echo
    echo "You can now use the 'cryodl' command from anywhere:"
    echo "  cryodl --help                    # Show help"
    echo "  cryodl init                      # Initialize configuration"
    echo "  cryodl show                      # Show current configuration"
    echo
    echo "For more information, visit: https://github.com/shenlab/cryoDL"
else
    echo "Error: cryoDL CLI was not installed properly"
    echo "Please check the installation output above for errors"
    exit 1
fi
