# Olympic Athletes and Longevity

## Overview

### Motivation

In May 2026, I came across a remarkable news story on NOS about a tennis match at Roland Garros. Czech tennis player Jakub Mensik had won his match, but afterwards he collapsed due to severe cramping and dehydration. He was eventually taken off the court in a wheelchair because he was unable to stand. Temperatures on the court had reached 32°C, and the match had lasted more than four hours.

Fortunately, Mensik had recovered sufficiently to play his next match. However, the incident made me think about the extreme physical demands placed on professional athletes. Stories about athletes competing under extreme conditions and suffering injuries are not uncommon. In rare cases, athletes even die as a result of the physical demands of their sport. In their pursuit of excellence, elite athletes sometimes push their bodies beyond what is healthy.

This raised a question: **Could the physical demands of elite sports have long-term consequences for athletes' health and longevity?**

More specifically, I wondered whether people who have competed at the highest level tend to die younger than the general population.

To investigate this question, I needed a sufficiently large group of athletes for whom historical participation records were available. I decided to focus on Olympic athletes, as the Olympic Games provide a large population of elite athletes across many sports and generations.

### Research Goal

The main goal of this project is to investigate whether there is evidence that Olympic athletes have shorter lifespans than comparable individuals in the general population.

The initial hypothesis is that participation in elite sports may be associated with reduced longevity. However, the analysis is intended to investigate this possibility rather than assume that the hypothesis is correct.

In addition to comparing Olympic athletes with the general population, I plan to explore differences within the Olympic athlete population. These include comparisons between medal winners and non-medal winners, men and women, Summer and Winter Olympians, and athletes competing in team versus individual sports.

The project combines historical Olympic participation records with biographical information, including birthdates and deathdates, to investigate these questions.

## Research Questions

The main research question is:

**Do Olympic athletes have different lifespans from comparable individuals in the general population?**

Potential additional questions include:

- Does longevity differ between medal winners and non-medal winners?
- Are there differences between male and female athletes?
- Does longevity differ between Summer and Winter Olympians?
- Are there differences between athletes competing in team and individual sports?
- Does longevity vary between different sports?
- Is longevity associated with participation in multiple Olympic Games?
- Do results vary between countries or historical periods?
- Do the recorded causes of death differ between Olympic athletes and the general population, or between different groups of Olympic athletes?

These questions are intended for future investigation and have not yet been answered. The feasibility of investigating causes of death will depend on the availability and reliability of the data, as many athletes have no recorded cause of death in Wikidata.

## Data Sources

The project currently uses the following sources:

- **Olympic participation data:** [120 Years of Olympic History](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results), containing information about athletes, Olympic Games, sports, countries, and medals from 1896 to 2016.
- **Olympedia datasets:** [Keith Galli's Olympics-Dataset](https://github.com/KeithGalli/Olympics-Dataset), containing data scraped from [Olympedia](https://www.olympedia.org/). Two files are used:
  - `athletes/bios.csv` — Biographical information and identifiers for Olympic athletes.
  - `results/results.csv` — Olympic event results and participation records, used together with the biographical data to help match athletes to the Kaggle dataset.
- **Biographical information:** [Wikidata](https://www.wikidata.org/), used to retrieve athletes' birthdates, deathdates, recorded causes of death, and other identifying information.

An important consideration is that an athlete may have participated in multiple Olympic Games, sports, or events. Individual participation records therefore do not necessarily represent unique athletes.

Additional data sources will be needed to compare Olympic athletes' lifespans with those of the general population.

## Current Features

### Olympic data processing

- Load and prepare Olympic participation data from a CSV file.
- Create separate binary columns for gold, silver, and bronze medals.
- Filter records by medal type and Olympic year.
- Retrieve unique athletes and filter records by selected athletes.
- Combine filtering operations.
- Test filtering functionality using pytest.

### Biographical data collection

- Search Wikidata for Olympic athletes using names and name variations.
- Retrieve Wikidata identifiers and available birthdates, deathdates, and recorded causes of death.
- Retrieve information about whether an athlete is classified as living or deceased.
- Record diagnostic information when scraping or matching problems occur.

The initial matching procedure selects the first Wikidata search result. This is a known limitation and an important focus of future development.

### Data-quality analysis

An exploratory analysis has been completed to investigate the reliability and availability of biographical information retrieved from Wikidata.

The analysis examines three questions:

1. Whether the number of Wikidata search results is associated with chronological inconsistencies.
2. How the availability of biographical information varies across Olympic generations.
3. How the frequency and types of chronological inconsistencies vary between Olympic decades.

The analysis uses a preliminary sample of 5,693 athletes.

**Key findings:**

- Athletes whose names return multiple Wikidata search results are more likely to have detected chronological inconsistencies.
- The availability of biographical information and life-status classifications varies across Olympic generations.
- Chronological inconsistencies are generally more frequent among earlier Olympic generations, although differences in data availability and sample sizes affect interpretation.

Chronological inconsistencies may indicate incorrect identity matches, but they do not prove that the selected Wikidata entry belongs to the wrong person.

The full methodology, results, and limitations are documented in the exploratory analysis notebook.

## Project Structure

The project is organized into a Python package containing the core functionality, alongside datasets, Jupyter notebooks, and automated tests.

The main components are:

- `unhealthy_athletes/` — Python package containing the project's core functionality:
  - `olympic_data.py` — Loading and preparing Olympic participation data.
  - `analysis.py` — Filtering and analyzing Olympic participation records.
  - `prepare_for_scraping.py` — Preparing athlete information for biographical data collection.
  - `biography_scraper.py` — Retrieving biographical information from Wikidata.
  - `processing.py` — Processing and transforming collected biographical data.
  - `workflow.py` — Coordinating scraping, batching, validation, and saving results.
- `main.py` — Entry point for running the data collection workflow.
- `data/` — Input datasets and generated results, most of which are excluded from Git.
- `notebooks/` — Exploratory analyses and visualizations.
- `tests/` — Automated tests using pytest.
- `requirements.txt` — Python dependencies required by the project.


## Requirements

The project requires Python 3 and the dependencies listed in `requirements.txt`.

The main libraries include:

- pandas and NumPy for data processing.
- requests for retrieving information from Wikidata.
- python-dateutil for handling dates.
- Matplotlib for visualization.
- pytest for automated testing.
- JupyterLab for exploratory analysis.

Install the dependencies using:

```bash
python -m pip install -r requirements.txt
```

Some notebooks may require additional dependencies.

## Getting Started

### 1. Prepare the environment

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Lotte0906/unhealthy-athletes.git
cd unhealthy-athletes
```

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

### 2. Download the datasets

The project requires three CSV files. Download them from the following sources:

| File | Download source |
|---|---|
| `athlete_events.csv` | [120 Years of Olympic History (Kaggle)](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) |
| `bios.csv` | [Olympics-Dataset — athletes/bios.csv](https://github.com/KeithGalli/Olympics-Dataset/blob/master/athletes/bios.csv) |
| `results.csv` | [Olympics-Dataset — results/results.csv](https://github.com/KeithGalli/Olympics-Dataset/blob/master/results/results.csv) |

Place all three files directly inside the `data/` directory:

```text
data/
├── athlete_events.csv
├── bios.csv
└── results.csv
```

The datasets are not included in this repository. They must be downloaded separately before running the data collection workflow.

The Olympedia-derived files were verified against the versions used during development by comparing column names, row counts, and DataFrame contents.

### 3. Run the data collection workflow

From the project root, run:

```bash
python main.py
```

This is the entry point for the data collection workflow, which coordinates Olympic data preparation and biographical information retrieval.

The scraping process makes requests to external services and may take considerable time, depending on the number of athletes being processed.

#### Scraping configuration

The scraping workflow is configured in `main.py`:

```python
run_scraping(
    olympic_data,
    all_athletes,
    n_batches=500,
    reference_date=date(2026, 11, 13),
    adopt_legacy=False,
)
```

The parameters control how biographical data is collected and how previously generated results are handled:

- **`n_batches=500`** divides the athlete population into 500 batches, allowing the scraping process to be resumed without repeating all previous work.
- **`reference_date=date(2026, 11, 13)`** specifies the date used when calculating the ages of living athletes. A fixed reference date makes results reproducible across runs.
- **`adopt_legacy=False`** prevents older batch files without compatible metadata from being automatically accepted.

The workflow saves batch results and accompanying metadata in the `data/` directory. Existing batches are validated before reuse, and incompatible results are not automatically overwritten.

These settings reflect the current development configuration and can be adjusted in `main.py`. Changing the batch count or reference date may make previously generated batches incompatible with the new configuration.

**Note:** Running `main.py` starts the biographical collection workflow, which makes requests to Wikidata. Depending on the number of athletes and previously completed batches, execution may take considerable time.

### 4. Run the tests

```bash
python -m pytest -v
```

### 5. Explore the analysis

The Jupyter notebooks contain the exploratory analysis and visualizations. Some notebooks may require intermediate datasets generated by the scraping pipeline.

## Notebook Guide

The `notebooks/` directory contains exploratory analyses and experiments that support the development of this project.

The following notebooks are included in the repository:

| Notebook | Description |
|---|---|
| [`name_matching.ipynb`](notebooks/name_matching.ipynb) | Explores matching athletes between the Kaggle and Olympedia datasets using normalized names and Olympic participation years. |
| [`scraping_analysis.ipynb`](notebooks/scraping_analysis.ipynb) | Investigates scraping results, missing biographical information, error messages, and potential data-quality problems. |
| [`wikidata_quality_report.ipynb`](notebooks/wikidata_quality_report.ipynb) | Presents a structured exploratory analysis of Wikidata matching reliability, biographical completeness, and chronological inconsistencies. |

### Reproducing the analyses

Some notebooks depend on intermediate datasets generated by the scraping workflow. These datasets are excluded from Git and must be generated locally before the corresponding analyses can be reproduced.

The notebooks document different stages of the project's development. Some exploratory code may reflect earlier implementations and may require adjustments to work with the current package structure.

The Wikidata quality report presents preliminary findings from a sample of 5,693 athletes. These findings are intended to identify data-quality issues and guide further development, rather than establish conclusions about Olympic athletes' longevity.

Personal experiments, temporary tests, and development notebooks are kept locally and excluded from Git through `.gitignore`.

## Future Development

The next priority is to improve the reliability of Wikidata identity matching.

Planned work includes:

- Evaluate multiple Wikidata candidates rather than automatically selecting the first search result.
- Use additional biographical and Olympic participation information to identify likely matches.
- Compare the improved matching procedure with the initial implementation.
- Extend biographical data collection to the remaining athletes.
- Investigate athletes' lifespans and compare them with suitable reference populations.
- Explore differences by sport, gender, country, and Olympic participation history.
- Consider survival analysis to account for athletes who are still alive.
- Assess the completeness and reliability of recorded causes of death and investigate whether the available data can support further analysis.

The long-term goal is to develop a reliable dataset and use it to investigate the relationship between elite athletic participation and longevity.