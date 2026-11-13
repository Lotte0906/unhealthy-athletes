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
- **Biographical information:** [Wikidata](https://www.wikidata.org/), used to retrieve athletes' birthdates, deathdates, recorded causes of death, and other identifying information.
- **Athlete identification:** [Olympedia](https://www.olympedia.org/), used to support the identification of Olympic athletes.

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

The repository contains Python modules for Olympic data processing, filtering, biographical scraping, and analysis, alongside Jupyter notebooks and automated tests.

The main components include:

- `olympic_data.py` — Loading and preparing Olympic participation data.
- analysis.py — Filtering Olympic participation records by medal type and year, and supporting further analysis.
- prepare_for_scraping.py — Selecting athletes for biographical data collection.- `biography_scraper.py` — Retrieving biographical information from Wikidata, including information used to detect potential identity-matching errors.
- `processing.py` — Processing and transforming collected data.
- `workflow.py` — Coordinating the biographical data collection pipeline, including batching, scraping, processing, and saving results.
- `main.py` — Providing the entry point for running the data collection workflow.
- `notebooks/` — Containing exploratory analyses and visualizations.
- `tests/` — Containing automated tests.

## Requirements

The project uses Python and several libraries for data processing, HTTP requests, testing, and visualization.

The main libraries include:

- pandas
- NumPy
- requests
- Matplotlib
- pytest
- Jupyter
- python-dateutil

Additional dependencies may be required for specific notebooks.

## Getting Started

### 1. Prepare the environment

Install Python and the required libraries.

For example, the main libraries can be installed using:

```bash
python -m pip install pandas numpy requests matplotlib pytest jupyterlab python-dateutil
```

### 2. Download the Olympic dataset

Download `athlete_events.csv` from the [Kaggle dataset page](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) and place it in the `data/` directory.

The dataset is not included in the repository.

### 3. Run the data collection workflow

From the project root, run:

```bash
python main.py
```

This is the entry point for the data collection workflow, which coordinates Olympic data preparation and biographical information retrieval.

The scraping process makes requests to external services and may take considerable time, depending on the number of athletes being processed.

### 4. Run the tests

```bash
python -m pytest -v
```

### 5. Explore the analysis

The Jupyter notebooks contain the exploratory analysis and visualizations. Some notebooks may require intermediate datasets generated by the scraping pipeline.

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