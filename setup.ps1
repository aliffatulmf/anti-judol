#!/usr/bin/env pwsh -NoLogo

$ErrorActionPreference = "Stop"

Write-Host "Setting up environment for Open-JUDOL..." -ForegroundColor Green

if (-not [Environment]::Is64BitOperatingSystem) {
    Write-Host "Error: This script is only for x86_64 architecture" -ForegroundColor Red
    Write-Host "32-bit systems are not supported" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -Path "./bin")) {
    Write-Host "Creating bin directory..." -ForegroundColor Cyan
    New-Item -Path "./bin" -ItemType Directory | Out-Null
}

Write-Host "Installing uv using the official installer..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install.ps1
    ./install.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install uv" -ForegroundColor Red
        exit 1
    }
    Remove-Item -Path install.ps1 -Force
}
catch {
    Write-Host "Error: Failed to install uv: $_" -ForegroundColor Red
    exit 1
}

$env:PATH = "$HOME\.local\bin;$env:PATH"

try {
    $null = & uv --version
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: uv installation failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "uv installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Error: uv installation failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Creating virtual environment with Python 3.11..." -ForegroundColor Cyan
if (Test-Path -Path ".venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Path ".venv" -Recurse -Force
}

try {
    & uv venv -p 3.11 --seed .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error: Failed to create virtual environment: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
try {
    & .venv\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error: Failed to activate virtual environment: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan

if (Test-Path -Path "pyproject.toml") {
    Write-Host "Found pyproject.toml, using uv sync to install dependencies..." -ForegroundColor Cyan

    Write-Host "Creating/updating lockfile..." -ForegroundColor Cyan
    try {
        & uv lock
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to create/update lockfile" -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host "Error: Failed to create/update lockfile: $_" -ForegroundColor Red
        exit 1
    }

    if ($args -contains "--dev") {
        Write-Host "Installing with development dependencies..." -ForegroundColor Cyan
        try {
            & uv sync --all-extras
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error: Failed to sync environment with development dependencies" -ForegroundColor Red
                exit 1
            }
        }
        catch {
            Write-Host "Error: Failed to sync environment with development dependencies: $_" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "Installing standard dependencies..." -ForegroundColor Cyan
        try {
            & uv sync
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error: Failed to sync environment" -ForegroundColor Red
                exit 1
            }
        }
        catch {
            Write-Host "Error: Failed to sync environment: $_" -ForegroundColor Red
            exit 1
        }
    }
}
else {
    Write-Host "Error: No pyproject.toml found. Cannot install dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The virtual environment has been activated." -ForegroundColor Green
Write-Host "You can now run the application." -ForegroundColor Green
