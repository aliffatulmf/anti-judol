# YouTube Anti-JUDOL

**⚠️ WARNING: THIS PROJECT IS UNTESTED ⚠️**

Anti-JUDOL is a tool for monitoring and classifying YouTube comments, particularly those potentially promoting online gambling. This project is in early development stage and has not been thoroughly tested.

## Description

This project was developed to help monitor YouTube comments automatically with the ability to:

- Extract comments from YouTube videos
- Classify comments using machine learning models
- ~~Save results in CSV format for further analysis~~

## Features

- YouTube comment scraping using SeleniumBase
- Comment classification with machine learning models (optional)
- Comment sorting by "newest" or "top"
- Text normalization for Indonesian language using nlp-id
- Graceful interruption handling (Ctrl+C) with automatic saving

## Requirements

- Python 3.11 or higher
- 64-bit operating system (Windows or Linux)
- Python dependencies (see `pyproject.toml` or `requirements.txt`)

Note: The application will automatically download and set up a Chromium browser during the first run.

## Installation

### Automatic Setup (Recommended)

The project includes setup scripts for both Windows and Linux that will automatically:
- Check if you're running on a 64-bit system (required)
- Download and install uv (Python package manager)
- Create a virtual environment with Python 3.11
- Install all dependencies
- Activate the virtual environment

#### Windows

```powershell
# Run the PowerShell setup script
.\setup.ps1

# For development setup with additional tools
.\setup.ps1 --dev
```

#### Linux

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# For development setup with additional tools
./setup.sh --dev
```

### Manual Installation

If you prefer to set up manually:

```bash
# Clone repository
git clone https://github.com/username/anti-judol.git
cd anti-judol

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## Usage

### Running Anti-JUDOL

After setting up the environment, you can run the main application:

```bash
# Activate the virtual environment if not already activated
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Run the main application
python anti_judol.py --help
```

### Authentication

Before using the comment removal features, you need to log in to your YouTube account:

```bash
python anti_judol.py --login
```

This will open a browser window where you can log in to your YouTube account. The login session will be saved for future use.

### Removing Comments

You can remove comments from specific videos:

```bash
# Remove comments from specific URLs
python anti_judol.py --remove_urls "https://www.youtube.com/watch?v=VIDEO_ID1" "https://www.youtube.com/watch?v=VIDEO_ID2"

# Remove comments from URLs listed in a text file
python anti_judol.py --remove_txt "urls.txt"
```

### Checking Login Status

```bash
python anti_judol.py --status
```

### Scraping YouTube Comments

You can also use the YouTube comment scraper directly:

```bash
python youtube_scraper.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output "output/comments.csv" --sort_by "top"
```

#### Scraper Parameters

- `--url`: YouTube video URL (required)
- `--output`: Path to save the CSV result file (default: "temp/comments.csv")
- `--sort_by`: Comment order ("newest" or "top", default: "top")
- `--model`: Path to model file for classification (optional)

## Browser Download Process

When you run `anti_judol.py` for the first time, the application will automatically:

1. Check if a Chrome/Chromium browser is already installed in the `bin/chrome` directory
2. If not found, it will:
   - Create a `bin` directory if it doesn't exist
   - Download the appropriate Chromium version for your operating system (Windows or Linux)
   - Extract the browser to the `bin/chrome` directory
   - Create a `bin/User Data` directory for storing browser profile data
3. The browser will be used for YouTube authentication and comment removal

This process ensures that you don't need to manually install a browser, and the application will use a consistent browser version across different environments.

## Project Structure

```
anti-judol/
├── anti_judol/
│   ├── actions/
│   │   ├── auth.py             # YouTube authentication
│   │   └── remover.py          # Comment removal functionality
│   ├── download.py             # Browser downloader
│   ├── model.py                # Model loading and inference
│   └── normalizer.py           # Text normalization
├── bin/                        # Directory for browser and user data
│   ├── chrome/                 # Downloaded browser files
│   └── User Data/              # Browser profile data
├── data/
│   └── models/                # Trained models
├── anti_judol.py              # Main application script
├── youtube_scraper.py         # YouTube comment scraper
├── setup.ps1                  # Windows setup script
├── setup.sh                   # Linux setup script
└── pyproject.toml             # Project configuration and dependencies
```

## Development Status

This project is still in early development stage and **HAS NOT BEEN THOROUGHLY TESTED**. Some features may not work as expected. Use at your own risk.

## Security and Testing

### Data Security
- This project is engineered with user security in mind: all operations run locally on your computer without transmitting credential data to external servers.
- When logging into YouTube, credentials are stored only in the local `bin/User Data` directory and are never sent to developers or other third parties.
- Nevertheless, always review the source code before running applications that request access to your social media accounts.

### Testing Status
- Currently, the project has not been tested on YouTube videos that actually contain online gambling (JUDOL) comments.
- Testing has only been performed with simulated data and has not been verified in a real production environment.
- We plan to conduct comprehensive testing with real-world cases in the future to ensure the effectiveness of JUDOL comment detection and removal.
