#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Setting up environment for Anti-Judol..."
echo "This script will:
 - Check if running on Linux x64 (64-bit system required)
 - Download and install uv (Python package manager)
 - Create a virtual environment with Python 3.11
 - Install dependencies using uv sync (creates lockfile and installs packages)
 - Activate the virtual environment"
echo ""

# Check if running on Linux
OS="$(uname -s)"
if [[ "$OS" != "Linux" ]]; then
    echo "Error: This script is only for Linux systems"
    exit 1
fi

# Check if architecture is x86_64
ARCH="$(uname -m)"
if [[ "$ARCH" != "x86_64" ]]; then
    echo "Error: This script is only for x86_64 architecture"
    echo "32-bit systems are not supported"
    exit 1
fi

# Additional check for 64-bit system
if [ "$(getconf LONG_BIT)" != "64" ]; then
    echo "Error: This script requires a 64-bit operating system"
    echo "Your system reports as $(getconf LONG_BIT)-bit"
    exit 1
fi

echo "Detected OS: Linux, Architecture: x86_64"

# Create bin directory if it doesn't exist
if [ ! -d "./bin" ]; then
    echo "Creating bin directory..."
    mkdir -p ./bin
fi

# Set UV download URL for Linux x86_64
UV_ASSET_ID="244348594"  # Linux x86_64

echo "Downloading uv..."

# Check for required tools
for cmd in curl jq unzip; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is not installed. Please install it first."
        echo "On Debian/Ubuntu: sudo apt-get install $cmd"
        echo "On Fedora: sudo dnf install $cmd"
        exit 1
    fi
done

# Download uv
UV_DOWNLOAD_URL=$(curl -s "https://api.github.com/repos/astral-sh/uv/releases/assets/$UV_ASSET_ID" | jq -r '.browser_download_url')

if [ -z "$UV_DOWNLOAD_URL" ] || [ "$UV_DOWNLOAD_URL" == "null" ]; then
    echo "Error: Failed to get download URL for uv"
    exit 1
fi

echo "Downloading uv from $UV_DOWNLOAD_URL"
curl -L -o "./bin/uv.zip" "$UV_DOWNLOAD_URL"

# Extract uv
echo "Extracting uv..."
rm -rf ./bin/uv  # Remove existing uv directory if it exists
mkdir -p ./bin/uv
unzip -q ./bin/uv.zip -d ./bin/uv

# Make uv executable
chmod +x ./bin/uv/uv

# Remove zip file
rm ./bin/uv.zip

# Add uv to PATH temporarily
export PATH="$PWD/bin/uv:$PATH"

# Check if uv is working
if ! command -v uv &> /dev/null; then
    echo "Error: uv installation failed"
    exit 1
fi

echo "uv installed successfully"

# Create virtual environment
echo "Creating virtual environment with Python 3.11..."
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

uv venv -p 3.11 --seed

# Install dependencies
echo "Installing dependencies..."

# Check for pyproject.toml first (preferred method)
if [ -f "pyproject.toml" ]; then
    echo "Found pyproject.toml, using uv sync to install dependencies..."

    # Create or update lockfile
    echo "Creating/updating lockfile..."
    uv lock
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create/update lockfile"
        exit 1
    fi

    # Sync environment based on development mode
    if [ "$1" = "--dev" ]; then
        echo "Installing with development dependencies..."
        # Install with all extras and development dependencies
        uv sync --all-extras
        if [ $? -ne 0 ]; then
            echo "Error: Failed to sync environment with development dependencies"
            exit 1
        fi

        # Ensure pytest is available
        if ! python -c "import pytest" &>/dev/null; then
            echo "Installing pytest..."
            uv pip install pytest pytest-cov
        fi
    else
        # Standard installation without development dependencies
        echo "Installing standard dependencies..."
        uv sync
        if [ $? -ne 0 ]; then
            echo "Error: Failed to sync environment"
            exit 1
        fi
    fi
# Fallback to requirements.txt if no pyproject.toml
elif [ -f "requirements.txt" ]; then
    echo "Found requirements.txt, installing dependencies..."
    uv pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies from requirements.txt"
        exit 1
    fi

    # Install development dependencies if in development mode
    if [ "$1" = "--dev" ] && [ -f "requirements-dev.txt" ]; then
        echo "Installing development dependencies from requirements-dev.txt..."
        uv pip install -r requirements-dev.txt
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install development dependencies"
            exit 1
        fi

        # Ensure pytest is available
        if ! python -c "import pytest" &>/dev/null; then
            echo "Installing pytest..."
            uv pip install pytest pytest-cov
        fi
    fi
else
    echo "Warning: No pyproject.toml or requirements.txt found. Skipping dependency installation."
fi

# Activate virtual environment instructions
echo ""
echo "Setup completed successfully!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "After activation, you can run the application with:"
echo "  python anti_judol.py --help"
echo ""
echo "For development setup, run this script with the --dev flag:"
echo "  ./setup.sh --dev"

# Attempt to activate the virtual environment automatically
echo ""
echo "Attempting to activate virtual environment automatically..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated. You can now run the application."

    # Check Python version
    PYTHON_VERSION=$(python --version 2>&1)
    echo "Using $PYTHON_VERSION"

    # Check if uv is available in the virtual environment
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version 2>&1)
        echo "Using uv version: $UV_VERSION"
    else
        echo "Warning: uv not found in PATH after activation"
    fi
else
    echo "Could not activate virtual environment automatically."
    echo "Please activate it manually using the command above."
fi
