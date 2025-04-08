# PowerShell script for setting up Anti-Judol environment on Windows
# This script downloads uv, creates a virtual environment, and installs dependencies using uv sync

$ErrorActionPreference = "Stop"  # Stop on first error

Write-Host "Setting up environment for Anti-Judol..." -ForegroundColor Green
Write-Host "This script will:
 - Check if running on a 64-bit system (required)
 - Download and install uv (Python package manager)
 - Create a virtual environment with Python 3.11
 - Install dependencies using uv sync (creates lockfile and installs packages)
 - Activate the virtual environment" -ForegroundColor Cyan
Write-Host ""

# Check if running on 64-bit system
if (-not [Environment]::Is64BitOperatingSystem) {
    Write-Host "Error: This script requires a 64-bit operating system" -ForegroundColor Red
    Write-Host "32-bit systems are not supported" -ForegroundColor Red
    exit 1
}

# Create bin directory if it doesn't exist
if (-not (Test-Path -Path ".\bin")) {
    Write-Host "Creating bin directory..." -ForegroundColor Cyan
    New-Item -Path ".\bin" -ItemType Directory | Out-Null
}

Write-Host "Downloading uv for Windows..." -ForegroundColor Cyan

# Asset ID for Windows x86_64
$UV_ASSET_ID = "244348593"

# Download uv
try {
    $UV_DOWNLOAD_URL = (Invoke-RestMethod -Uri "https://api.github.com/repos/astral-sh/uv/releases/assets/$UV_ASSET_ID").browser_download_url

    if (-not $UV_DOWNLOAD_URL) {
        Write-Host "Error: Failed to get download URL for uv" -ForegroundColor Red
        exit 1
    }

    Write-Host "Downloading uv from $UV_DOWNLOAD_URL" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $UV_DOWNLOAD_URL -OutFile ".\bin\uv.zip"
}
catch {
    Write-Host "Error downloading uv: $_" -ForegroundColor Red
    exit 1
}

# Extract uv
Write-Host "Extracting uv..." -ForegroundColor Cyan
if (Test-Path -Path ".\bin\uv") {
    Remove-Item -Path ".\bin\uv" -Recurse -Force
}
New-Item -Path ".\bin\uv" -ItemType Directory | Out-Null

try {
    Expand-Archive -Path ".\bin\uv.zip" -DestinationPath ".\bin\uv" -Force
    Remove-Item -Path ".\bin\uv.zip" -Force
}
catch {
    Write-Host "Error extracting uv: $_" -ForegroundColor Red
    exit 1
}

# Add uv to PATH temporarily
$env:PATH = "$PWD\bin\uv;$env:PATH"

# Check if uv is working
try {
    $null = Get-Command "uv.exe" -ErrorAction Stop
    Write-Host "uv installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Error: uv installation failed" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment with Python 3.11..." -ForegroundColor Cyan
if (Test-Path -Path ".\.venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Path ".\.venv" -Recurse -Force
}

try {
    & uv venv -p 3.11 --seed
}
catch {
    Write-Host "Error creating virtual environment: $_" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan

# Check for pyproject.toml first (preferred method)
if (Test-Path -Path ".\pyproject.toml") {
    Write-Host "Found pyproject.toml, using uv sync to install dependencies..." -ForegroundColor Cyan

    # Create or update lockfile
    Write-Host "Creating/updating lockfile..." -ForegroundColor Cyan
    try {
        & uv lock
    }
    catch {
        Write-Host "Error: Failed to create/update lockfile: $_" -ForegroundColor Red
        exit 1
    }

    # Sync environment based on development mode
    if ($args -contains "--dev") {
        Write-Host "Installing with development dependencies..." -ForegroundColor Cyan
        # Install with all extras and development dependencies
        try {
            & uv sync --all-extras
        }
        catch {
            Write-Host "Error: Failed to sync environment with development dependencies: $_" -ForegroundColor Red
            exit 1
        }

        # Ensure pytest is available
        try {
            & python -c "import pytest" 2>$null
        }
        catch {
            Write-Host "Installing pytest..." -ForegroundColor Cyan
            & uv pip install pytest pytest-cov
        }
    }
    else {
        # Standard installation without development dependencies
        Write-Host "Installing standard dependencies..." -ForegroundColor Cyan
        try {
            & uv sync
        }
        catch {
            Write-Host "Error: Failed to sync environment: $_" -ForegroundColor Red
            exit 1
        }
    }
}
# Fallback to requirements.txt if no pyproject.toml
elseif (Test-Path -Path ".\requirements.txt") {
    Write-Host "Found requirements.txt, installing dependencies..." -ForegroundColor Cyan
    try {
        & uv pip install -r requirements.txt
    }
    catch {
        Write-Host "Error: Failed to install dependencies from requirements.txt: $_" -ForegroundColor Red
        exit 1
    }

    # Install development dependencies if in development mode
    if ($args -contains "--dev" -and (Test-Path -Path ".\requirements-dev.txt")) {
        Write-Host "Installing development dependencies from requirements-dev.txt..." -ForegroundColor Cyan
        try {
            & uv pip install -r requirements-dev.txt
        }
        catch {
            Write-Host "Error: Failed to install development dependencies: $_" -ForegroundColor Red
            exit 1
        }

        # Ensure pytest is available
        try {
            & python -c "import pytest" 2>$null
        }
        catch {
            Write-Host "Installing pytest..." -ForegroundColor Cyan
            & uv pip install pytest pytest-cov
        }
    }
}
else {
    Write-Host "Warning: No pyproject.toml or requirements.txt found. Skipping dependency installation." -ForegroundColor Yellow
}

# Activation instructions
Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "After activation, you can run the application with:" -ForegroundColor Cyan
Write-Host "  python anti_judol.py --help" -ForegroundColor White
Write-Host ""
Write-Host "For development setup, run this script with the --dev flag:" -ForegroundColor Cyan
Write-Host "  .\setup.ps1 --dev" -ForegroundColor White

# Attempt to activate the virtual environment automatically
Write-Host ""
Write-Host "Attempting to activate virtual environment automatically..." -ForegroundColor Cyan

# Check both possible virtual environment paths
$venvPath = ".\venv\Scripts\Activate.ps1"
$dotVenvPath = ".\.venv\Scripts\Activate.ps1"

if (Test-Path -Path $venvPath) {
    $activateScript = $venvPath
    Write-Host "Found virtual environment at venv/" -ForegroundColor Cyan
}
elseif (Test-Path -Path $dotVenvPath) {
    $activateScript = $dotVenvPath
    Write-Host "Found virtual environment at .venv/" -ForegroundColor Cyan
}
else {
    $activateScript = $null
    Write-Host "Could not find virtual environment activation script" -ForegroundColor Yellow
}

# Activate the virtual environment if found
if ($activateScript -ne $null) {
    # Activate the virtual environment
    try {
        . $activateScript
        Write-Host "Virtual environment activated. You can now run the application." -ForegroundColor Green

        # Check Python version
        $PYTHON_VERSION = & python --version
        Write-Host "Using $PYTHON_VERSION" -ForegroundColor Cyan

        # Check if uv is available in the virtual environment
        try {
            $UV_VERSION = & uv --version
            Write-Host "Using uv version: $UV_VERSION" -ForegroundColor Cyan
        }
        catch {
            Write-Host "Warning: uv not found in PATH after activation" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Error activating virtual environment: $_" -ForegroundColor Red
        Write-Host "Please activate it manually using the command above." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Could not find virtual environment activation script at $activateScript" -ForegroundColor Yellow
    Write-Host "Please activate it manually using the command above." -ForegroundColor Yellow
}
