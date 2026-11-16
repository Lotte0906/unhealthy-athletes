# Coordinates loading, batching, scraping, and saving

import datetime
from pathlib import Path
import hashlib
import json
from collections import Counter
import pandas as pd

from .olympic_data import OlympicData
from .name_matching import match_athletes
from .biography_scraper import (
    find_wikidata_entry,
    get_wikidata_claims
)
from .processing import (
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



# Increase this when scraping or processing changes make
# previously saved results incompatible.
PROCESSING_VERSION = 1

REQUIRED_BATCH_COLUMNS = {
    "ID",
    "qid",
    "birthdate",
    "deathdate",
    "status",
    "age",
    "errormessage",
    "birthdate_original",
    "deathdate_original",
    "birthdate_date_issue",
    "deathdate_date_issue",
}


def file_hash(path):
    """Calculate a SHA-256 hash of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def dataframe_hash(df):
    """Fingerprint DataFrame contents, including row order."""
    # Convert values to strings for a consistent JSON representation.
    records = [
        [None if pd.isna(value) else str(value) for value in row]
        for row in df.itertuples(index=False, name=None)
    ]

    content = json.dumps(
        {
            "columns": df.columns.tolist(),
            "rows": records,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_batch_file(path, expected_ids, required_columns):
    """Check that a CSV has the expected rows and columns."""
    try:
        df = pd.read_csv(path)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"{path} is missing columns: {sorted(missing)}"
        )

    if df["ID"].isna().any():
        raise ValueError(f"{path} contains missing athlete IDs")

    try:
        actual_ids = pd.to_numeric(
            df["ID"], errors="raise"
        ).astype("int64")

        if not (actual_ids == df["ID"]).all():
            raise ValueError("Non-integer athlete ID")

    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"{path} contains invalid athlete IDs"
        ) from exc

    if Counter(actual_ids.tolist()) != Counter(expected_ids):
        raise ValueError(
            f"{path} does not contain the expected athlete rows"
        )

    return df


def save_json_atomic(path, data):
    """Save JSON using a temporary file."""
    temporary = path.with_suffix(".tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    temporary.replace(path)


def run_scraping(
    olympic_data,
    all_athletes,
    n_batches=49,
    reference_date=None,
    adopt_legacy=False,
    output_dir="data",
):
    """
    Scrape biographies in resumable batches.

    Existing batches are validated before being skipped.
    Incompatible batches are never overwritten automatically.

    adopt_legacy=True allows structurally valid older CSVs
    without metadata to be registered for future runs.
    Their historical processing configuration cannot be verified.
    """
    if not isinstance(n_batches, int) or n_batches < 1:
        raise ValueError("n_batches must be a positive integer")

    if reference_date is None:
        reference_date = datetime.date.today()

    if isinstance(reference_date, str):
        reference_date = datetime.date.fromisoformat(reference_date)

    if not isinstance(reference_date, datetime.date):
        raise TypeError("reference_date must be a date or ISO date string")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total_athletes = len(all_athletes)
    batch_info = []

    # Prepare and validate every batch before starting any scraping.
    for batch_num in range(n_batches):
        start = batch_num * total_athletes // n_batches
        end = (batch_num + 1) * total_athletes // n_batches

        batch_athletes = all_athletes.iloc[start:end]

        original_rows = olympic_data[
            olympic_data["ID"].isin(batch_athletes["ID"])
        ]

        output_file = output_dir / (
            f"entries{batch_num + 1}of{n_batches}.csv"
        )
        metadata_file = output_file.with_suffix(".json")

        expected_ids = original_rows["ID"].tolist()

        # Both source tables contribute to the fingerprint.
        input_fingerprint = hashlib.sha256(
            (
                dataframe_hash(batch_athletes)
                + dataframe_hash(original_rows)
            ).encode("utf-8")
        ).hexdigest()

        expected_metadata = {
            "schema_version": 1,
            "processing_version": PROCESSING_VERSION,
            "batch_number": batch_num + 1,
            "n_batches": n_batches,
            "reference_date": reference_date.isoformat(),
            "input_fingerprint": input_fingerprint,
            "row_count": len(expected_ids),
        }

        batch_info.append({
            "athletes": batch_athletes,
            "output": output_file,
            "metadata": metadata_file,
            "expected_ids": expected_ids,
            "expected_metadata": expected_metadata,
        })

    # Preflight: do not start network requests if an existing
    # batch is incompatible with the current run.
    for batch in batch_info:
        output_file = batch["output"]
        metadata_file = batch["metadata"]

        if not output_file.exists():
            if metadata_file.exists():
                raise ValueError(
                    f"Metadata exists but CSV is missing: {output_file}"
                )
            continue

        validate_batch_file(
            output_file,
            batch["expected_ids"],
            REQUIRED_BATCH_COLUMNS,
        )

        if metadata_file.exists():
            with metadata_file.open("r", encoding="utf-8") as file:
                saved_metadata = json.load(file)

            for key, expected in batch["expected_metadata"].items():
                if saved_metadata.get(key) != expected:
                    raise ValueError(
                        f"Incompatible metadata for {output_file}: "
                        f"{key} differs. Existing results were preserved."
                    )

            if saved_metadata.get("output_hash") != file_hash(output_file):
                raise ValueError(
                    f"CSV changed since metadata was saved: {output_file}"
                )

        elif not adopt_legacy:
            raise ValueError(
                f"{output_file} has no metadata. "
                "Inspect the old results first. "
                "Use adopt_legacy=True only if you accept "
                "that their original processing version and "
                "reference date cannot be verified."
            )

    # All existing files passed the preflight checks.
    for batch in batch_info:
        output_file = batch["output"]
        metadata_file = batch["metadata"]
        metadata = batch["expected_metadata"].copy()

        if output_file.exists():
            if not metadata_file.exists():
                # Legacy adoption records what we checked,
                # not proof of the original processing settings.
                metadata["legacy_adopted"] = True
                metadata["provenance_verified"] = False
                metadata["output_hash"] = file_hash(output_file)

                save_json_atomic(metadata_file, metadata)

                print(
                    f"Adopted legacy batch: {output_file.name} "
                    "(original configuration unverified)"
                )

            print(f"Skipping validated batch: {output_file.name}")
            continue

        batch_athletes = batch["athletes"]

        print(
            f"Processing {output_file.name} "
            f"({len(batch_athletes)} athletes)"
        )

        df = process_batch(
            olympic_data,
            batch_athletes,
            reference_date,
        )

        # Validate the newly produced DataFrame before saving.
        missing = REQUIRED_BATCH_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"New batch is missing columns: {sorted(missing)}"
            )

        if Counter(df["ID"].tolist()) != Counter(
            batch["expected_ids"]
        ):
            raise ValueError(
                f"Unexpected athlete rows in {output_file.name}"
            )

        temporary_file = output_file.with_suffix(".tmp")

        df.to_csv(temporary_file, index=False)

        # Validate the actual serialized CSV as well.
        validate_batch_file(
            temporary_file,
            batch["expected_ids"],
            REQUIRED_BATCH_COLUMNS,
        )

        temporary_file.replace(output_file)

        metadata["legacy_adopted"] = False
        metadata["provenance_verified"] = True
        metadata["output_hash"] = file_hash(output_file)

        save_json_atomic(metadata_file, metadata)

        print(f"Completed {output_file.name}")
