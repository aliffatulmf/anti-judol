#!/bin/bash
set -e

OS="$(uname -s)"
if [[ "$OS" != "Linux" ]]; then
    echo "Error: This script is only for Linux systems"
    exit 1
fi

ARCH="$(uname -m)"
if [[ "$ARCH" != "x86_64" ]]; then
    echo "Error: This script is only for x86_64 architecture"
    echo "32-bit systems are not supported"
    exit 1
fi

if [ ! -d "./bin" ]; then
    echo "Creating bin directory..."
    mkdir -p ./bin
fi

echo "Installing uv using the official installer..."
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ $? -ne 0 ]; then
    echo "Error: Failed to install uv"
    exit 1
fi

export PATH="$HOME/.local/bin:$PATH"

echo "Creating virtual environment with Python 3.11..."
uv venv -p 3.11 --seed .venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Installing dependencies..."

if [ -f "pyproject.toml" ]; then
    echo "Found pyproject.toml, using uv sync to install dependencies..."

    echo "Creating/updating lockfile..."
    uv lock
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create/update lockfile"
        exit 1
    fi

    if [ "$1" = "--dev" ]; then
        echo "Installing with development dependencies..."
        uv sync --all-extras
        if [ $? -ne 0 ]; then
            echo "Error: Failed to sync environment with development dependencies"
            exit 1
        fi
    else
        echo "Installing standard dependencies..."
        uv sync
        if [ $? -ne 0 ]; then
            echo "Error: Failed to sync environment"
            exit 1
        fi
    fi
else
    echo "Error: No pyproject.toml found. Cannot install dependencies."
    exit 1
fi

echo "Setup completed successfully!"
echo ""
echo "IMPORTANT: To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
