# coordinates loading, batching, scraping, and saving



import datetime
import pandas as pd

from olympic_data import OlympicData
from name_matching import match_athletes
from biography_scraper_finding_errors import (
    find_wikidata_entry,
    get_wikidata_claims
)
from processing_finding_errors import (
    convert_dict_to_pd_df,
    merge_dataframes,
    convert_dates,
    add_age
)


def prepare_athletes():
    """Load Olympic data and match athletes to Olympedia."""

    olympics = OlympicData("data/athlete_events.csv")
    olympics.load_and_prepare()

    bios = pd.read_csv("data/bios.csv", usecols=["athlete_id", "Used name"])
    results = pd.read_csv("data/results.csv", usecols=["athlete_id", "Games"])

    # Match athletes using names and overlapping Olympic years.
    unique_matches, all_athletes = match_athletes(
        olympics.data, bios, results
    )

    # Save matching results separately.
    unique_matches.to_csv(
        "data/olympedia_name_matches.csv",
        index=False
    )

    all_athletes.to_csv(
        "data/olympedia_all_athletes.csv",
        index=False
    )

    # Use the corrected name when available.
    all_athletes["search_name"] = (
        all_athletes["olympedia_name"]
        .fillna(all_athletes["Name"])
    )

    # Add matching information to the original Olympic dataset.
    olympic_data = olympics.data.merge(
        all_athletes.drop(columns=["Name"]),
        on="ID",
        how="left",
        validate="many_to_one"
    )

    return olympic_data, all_athletes


def process_batch(olympic_data, batch_athletes, currentdate):
    """Scrape and process one batch of athletes."""

    # Keep all Olympic rows belonging to athletes in this batch.
    originaldf = olympic_data[
        olympic_data["ID"].isin(batch_athletes["ID"])
    ].copy()

    # Scrape each athlete once, using their preferred search name.
    person_entries = []

    for athlete in batch_athletes.itertuples(index=False):
        # Existing matching errors are passed into the scraper.
        initial_error = (
            athlete.errormessage
            if pd.notna(athlete.errormessage)
            else ""
        )

        person_entry = find_wikidata_entry(
            athlete.search_name,
            errormessage=initial_error
        )

        person_entry = get_wikidata_claims(person_entry)

        # Preserve the original Kaggle athlete ID.
        person_entry["ID"] = athlete.ID

        person_entries.append(person_entry)

    # Convert scraped dictionaries to a DataFrame.
    newdf = convert_dict_to_pd_df(person_entries)

    # The scraper now owns the accumulated error message.
    # Remove the original column to prevent duplicate error columns.
    originaldf = originaldf.drop(columns=["errormessage"])

    # Merge biographies using the athlete ID, not the name.
    df = merge_dataframes(originaldf, newdf)

    # Process dates and calculate ages.
    df = convert_dates(df)
    df = add_age(df, currentdate)

    return df


def run_scraping(olympic_data, all_athletes, n_batches=49):
    """Scrape athlete biographies and save the results in batches."""

    total_athletes = len(all_athletes)
    currentdate = datetime.date.today()

    for batch_num in range(n_batches):
        start = batch_num * total_athletes // n_batches
        end = (batch_num + 1) * total_athletes // n_batches

        batch_athletes = all_athletes.iloc[start:end]

        print(
            f"Processing batch {batch_num + 1}/{n_batches} "
            f"({len(batch_athletes)} athletes)"
        )

        df = process_batch(
            olympic_data,
            batch_athletes,
            currentdate
        )

        # Save results after each completed batch.
        df.to_csv(
            f"data/entries{batch_num + 1}of{n_batches}.csv",
            index=False
        )
