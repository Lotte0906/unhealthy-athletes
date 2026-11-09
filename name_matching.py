
import pandas as pd
import re


def normalize_name(name):
    """
    Normalize a name to match the formatting used in the Kaggle dataset.
    """
    if pd.isna(name):
        return ""

    name = str(name)

    # Replace Olympedia's name separator with a space.
    name = name.replace("•", " ")

    # Remove non-ASCII characters, as was done in the Kaggle dataset.
    name = name.encode("ascii", errors="ignore").decode("ascii")

    # Remove extra whitespace and convert to lowercase.
    name = re.sub(r"\s+", " ", name)

    return name.strip().lower()


def match_athletes(athletes, bios, results):
    """
    Match Kaggle athletes to Olympedia athletes using normalized names
    and overlapping Olympic years.

    Returns:
        unique_matches: Athletes with exactly one matching Olympedia ID.
        all_athletes: All Kaggle athletes, including unmatched and
                      ambiguous athletes, with an errormessage column.
    """

    # Create a table containing each Kaggle athlete once.
    kaggle = athletes[["ID", "Name"]].drop_duplicates()
    kaggle["normalized_name"] = kaggle["Name"].apply(normalize_name)

    # Create a table containing Olympedia athletes.
    olympedia = bios[["athlete_id", "Used name"]].copy()
    olympedia["normalized_name"] = olympedia["Used name"].apply(normalize_name)

    # Find the Olympic years in which each Kaggle athlete participated.
    kaggle_years = athletes[["ID", "Year"]].drop_duplicates()

    # Extract Olympic years from the Olympedia results dataset.
    olympedia_years = results[["athlete_id", "Games"]].drop_duplicates()

    olympedia_years["Year"] = pd.to_numeric(
        olympedia_years["Games"].str.extract(r"(\d{4})")[0],
        errors="coerce"
    )

    olympedia_years = olympedia_years[
        ["athlete_id", "Year"]
    ].drop_duplicates()

    # Find athletes whose normalized names match.
    matches = kaggle.merge(
        olympedia,
        on="normalized_name",
        how="inner"
    )

    # Keep only matches with at least one overlapping Olympic year.
    matches = matches.merge(kaggle_years, on="ID")
    matches = matches.merge(
        olympedia_years,
        on=["athlete_id", "Year"]
    )

    # Each Kaggle-Olympedia combination should appear only once.
    matches = matches.drop_duplicates(
        subset=["ID", "athlete_id"]
    )

    # Count the number of possible Olympedia matches for each athlete.
    candidate_counts = matches.groupby("ID")["athlete_id"].nunique()

    # Identify athletes with exactly one match.
    unique_ids = candidate_counts[
        candidate_counts == 1
    ].index

    unique_matches = matches[
        matches["ID"].isin(unique_ids)
    ].copy()

    # Identify athletes with multiple possible matches.
    ambiguous_ids = candidate_counts[
        candidate_counts > 1
    ].index

    # Rename the Olympedia name column.
    unique_matches = unique_matches.rename(
        columns={"Used name": "olympedia_name"}
    )

    # Replace the Olympedia name separator for readability.
    unique_matches["olympedia_name"] = (
        unique_matches["olympedia_name"]
        .str.replace("•", " ", regex=False)
    )

    # Keep only the columns needed for the unique matches dataset.
    unique_matches = unique_matches[
        ["ID", "Name", "athlete_id", "olympedia_name"]
    ]

    # Create a complete dataset containing every Kaggle athlete.
    all_athletes = kaggle[["ID", "Name"]].copy()

    # Add the unique Olympedia matches where available.
    all_athletes = all_athletes.merge(
        unique_matches[
            ["ID", "athlete_id", "olympedia_name"]
        ],
        on="ID",
        how="left"
    )

    # Assign an error message to athletes without a unique match.
    all_athletes["errormessage"] = "No reliable name match found"

    # Clear the error message for successfully matched athletes.
    all_athletes.loc[
        all_athletes["athlete_id"].notna(),
        "errormessage"
    ] = None

    # Assign a specific error message to ambiguous matches.
    all_athletes.loc[
        all_athletes["ID"].isin(ambiguous_ids),
        "errormessage"
    ] = "Multiple name matches found"

    # Check that every Kaggle athlete appears exactly once.
    assert all_athletes["ID"].is_unique

    return unique_matches, all_athletes
