# 🔗matchboxd🔗

**matchboxd** is a small Python script to quickly find movies overlapping between multiple lists or user watchlists.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [To-Do](#to-do)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)

## Introduction

**matchboxd** is a Python script designed to scrape and analyze Letterboxd movie lists and user watchlists. It identifies overlapping movies between multiple lists or watchlists and provides detailed information about each movie. This was a quick script I threw together in 2 hours one afternoon and is bound to be buggy and have errors, so bug reports, feedback, and feature requests are welcome. Additionally, while there does exist an API for Letterboxd, it is currently in private beta that I do not have access to, and the goal of my script does not seem to allign with the kind of development that they are open to. As such, this script makes great use of web scraping, so it should be used at your own risk.

## Features

- Fetch detailed information about each movie, including title, year, director, plot, average rating, and runtime.
- Output results to the console or save them to a CSV file.
- Option to run in fast mode, skipping extra film information fetching.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Braxt0n/matchboxd.git
    cd matchboxd
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Command Line Arguments

- `-l`, `--list`: Letterboxd list URL to use (can be specified multiple times).
- `-u`, `--user`: Letterboxd username to process their watchlist (can be specified multiple times).
- `-o`, `--output`: Output filename (CSV format).
- `-c`, `--count`: Minimum number of occurrences a film must appear in lists to be included. Will select the next lowest number if no films are found
- `-f`, `--fast`: Skip pulling extra film information.

### Examples

1. Scrape multiple user watchlists and save the results to a CSV file:
    ```sh
    python matchboxd.py -u user1 -u user2 -o results.csv
    ```

2. Scrape multiple lists and output results to the console:
    ```sh
    python matchboxd.py -l https://letterboxd.com/user/list/list1/ -l https://letterboxd.com/user/list/list2/
    ```

3. Scrape in fast mode and save the results to a CSV file:
    ```sh
    python matchboxd.py -u user1 -u user2 -l https://letterboxd.com/user/list/list1/ -o results.csv -f
    ```

## To-Do

- [ ] Add a quiet mode to suppress console output when generating a CSV file.
- [ ] Add support for other output formats (e.g., JSON).
- [ ] Improve error handling and reporting.
- [ ] Add unit tests for better code coverage.
- [ ] Optimize scraping performance with concurrent requests.
- [ ] JustWatch integration to filter by streaming service.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## Authors

- Braxton - [Braxt0n](https://github.com/yourusername)

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for more details.
