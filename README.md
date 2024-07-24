# LOL

![Language](https://img.shields.io/badge/Spellcheck-Pass-green?style=flat)
![Language](https://img.shields.io/badge/Language-Python-yellowgreen?style=flat)
![Testing](https://img.shields.io/badge/PEP8%20Check-Passing-green)
![Testing](https://img.shields.io/badge/Test-Pass-green)

## Description

This program 

## Requirements

python >= 3.8

**Setting Up the Environment**

* Windows: `./setup_Windows.bat`
* Linux/macOS: `./setup_Linux.sh`

These scripts will install required dependencies, and build a virtual environment for you if you don't have one.

## Running the Program

### CLI

1. Navigate to the `bin` directory: `cd bin`

To predict the result of a match:
2. Execute `python main.py [--help]` (use `python3` on Linux/macOS) in your terminal

    The `--help` flag displays available command-line arguments.

Else, if you want to get the latest data from the Riot API:
2. Execute `python manage_data.py --help` (use `python3` on Linux/macOS) in your terminal

    This will update the data in the `data` directory.

## Author

Neetre
