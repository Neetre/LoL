# LOL

![Language](https://img.shields.io/badge/Spellcheck-Pass-green?style=flat)
![Language](https://img.shields.io/badge/Language-Python-yellowgreen?style=flat)
![Testing](https://img.shields.io/badge/PEP8%20Check-Passing-green)
![Testing](https://img.shields.io/badge/Test-Pass-green)

## Description

This package is a tool for predicting the outcome of League of Legends matches. It uses data from the Riot API to train a machine learning model that predicts the outcome of matches based on various factors such as player performance, team composition, and game statistics.

Project Structure:

```plaintext
LOL/
├── bin/
│   ├── main.py
│   └── manage_data.py
├── data/
│   ├── champions_info_3.json
│   ├── game_{tier}.csv
|
├── LICENSE
├── README.md
├── setup_Windows.bat
├── setup_Linux.sh
├── requirements.txt
└── .gitignore
```

Main Features:

* Predict the outcome of a match, by using the main.py script.
* Update the data from the Riot API, by using the manage_data.py script.

To make the program work, you need to have a Riot API key. You can get one by following the instructions on the [Riot Developer Portal](https://developer.riotgames.com/).
When you have your API key, you need to create a file called `.env` in the root directory of the project, and add the following line to it:

```plaintext
RIOT_API_KEY="YOUR_API_KEY"
```

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

    The `--help` flag displays available command-line arguments.

## Author

Neetre
