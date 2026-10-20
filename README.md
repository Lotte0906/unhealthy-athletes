# Olympic Medal Winners Analysis

## Overview

This project explores Olympic medal-winning athletes using data from the [120 Years of Olympic History dataset on Kaggle](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results).

The goal is to investigate medal winners and eventually enrich the dataset with biographical information, such as birth and death dates, to explore athletes' lifespans.

The project is built in Python, using pandas to process and analyse the data.

## Current Features

- Load and prepare Olympic athlete data from a CSV file.
- Create separate binary columns for gold, silver, and bronze medals.
- Filter medal-winning records by medal type.
- Filter records by a range of Olympic years.
- Retrieve unique athlete names and filter records by selected athletes.
- Test filtering functions using pytest.

## Project Structure

```text
unhealthy_athletes/
├── data/
│   └── athlete_events.csv
├── notebooks/
│   └── exploration.ipynb
├── tests/
│   └── test_filtering.py
├── olympic_data.py
├── filtering.py
├── main.py
└── README.md
```

## Requirements

- Python
- pandas
- pytest (for running the tests)

## Getting Started

### 1. Install dependencies

From the project root, run:

```bash
python -m pip install pandas pytest
```

### 2. Prepare the data

Download `athlete_events.csv` from the [Kaggle dataset page](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) and place it in the `data/` directory.

### 3. Run the project

From the project root, run:

```bash
python main.py
```

The script loads and prepares the dataset, selects medal-winning records, filters them by year, and prints summary counts.

### 4. Run the tests

To run the test suite, execute:

```bash
python -m pytest -v
```

## Future Development

Planned extensions include:

- Collect biographical information about medal-winning athletes.
- Extract birth and death dates where available.
- Calculate athlete lifespans and analyse the resulting data.


Hypothesis:
Participating in elite Sports will shorten your lifetime



Plan of approach:
Get all medal winners from summer olympics in the 20th century and compare their life span.
Possibly also sorted by sport, country and gender.
Step 1. Webscrape all summer olympics medal winners to get the names of the athletes
Step 2. Webscrape all these names in wikipedia to get more information, including, but not limited to, their life span.
Step 3. Create a dataframe with the following columns:
    - Name
    - Sport
    - Birthday
    - Death day
    - Gender
    - Country
    - Participated Olympics
    - Kind of medal won
    
Step 4. Create visuals

Step 5. Create website
    
Note!! Someone can have participated in more than one sport and/or more than one year. Names will not be unique.
    
Some possible sub questions:
    - Difference in sport
    - Difference if participated more years
    - Difference if participated in more sports
    - Difference Gender
    - Difference in country
    - Difference in kind of medal
    - Difference in participated jaartal