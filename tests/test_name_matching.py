
import pytest
import pandas as pd

from name_matching import normalize_name, match_athletes


# --------------------------------------------------
# Fixtures
# --------------------------------------------------

@pytest.fixture
def test_data():
    """Create artificial Olympic datasets for testing name matching."""

    athletes = pd.DataFrame({
        "ID": [1, 1, 2, 3, 4, 5, 6],
        "Name": [
            "Jos Garca", "Jos Garca", "Anna Smith",
            "John Brown", "Jane Doe", "Peter Jones",
            "Maria Lopez"
        ],
        "Year": [2000, 2004, 2008, 2012, 1996, 1988, 2000]
    })

    bios = pd.DataFrame({
        "athlete_id": [101, 102, 103, 104, 105, 106, 107],
        "Used name": [
            "José García", "Anna Smith", "John Brown",
            "Jane Doe", "Jane Doe", "Peter Jones",
            "Someone Else"
        ]
    })

    results = pd.DataFrame({
        "athlete_id": [101, 101, 102, 103, 104, 105, 106, 107],
        "Games": [
            "2000 Summer", "2004 Summer", "2016 Summer",
            "2012 Summer", "1996 Summer", "1996 Summer",
            "1988 Summer", "2000 Summer"
        ]
    })

    return athletes, bios, results


@pytest.fixture
def matched_data(test_data):
    """Run name matching on the artificial datasets."""
    athletes, bios, results = test_data
    return match_athletes(athletes, bios, results)


# --------------------------------------------------
# Tests for normalize_name()
# --------------------------------------------------

def test_normalize_name_removes_accents():
    # Accented characters should be removed, not transliterated.
    assert normalize_name("José García") == "jos garca"


def test_normalize_name_replaces_separator():
    # Olympedia uses a bullet to separate parts of names.
    assert normalize_name("Anna•Maria Smith") == "anna maria smith"


def test_normalize_name_handles_whitespace():
    # Extra whitespace should be removed and names lowercased.
    assert normalize_name("  Anna   Maria Smith  ") == "anna maria smith"


def test_normalize_name_handles_missing_values():
    assert normalize_name(None) == ""
    assert normalize_name(float("nan")) == ""


# --------------------------------------------------
# Tests for match_athletes()
# --------------------------------------------------

def test_unique_match(matched_data):
    # Matching name and overlapping year should produce a unique match.
    unique_matches, all_athletes = matched_data

    match = unique_matches.loc[unique_matches["ID"] == 1].iloc[0]
    athlete = all_athletes.loc[all_athletes["ID"] == 1].iloc[0]

    assert match["athlete_id"] == 101
    assert match["olympedia_name"] == "José García"
    assert pd.isna(athlete["errormessage"])


def test_different_years_do_not_match(matched_data):
    # Matching names alone are insufficient if Olympic years differ.
    unique_matches, all_athletes = matched_data

    assert 2 not in unique_matches["ID"].values

    athlete = all_athletes.loc[all_athletes["ID"] == 2].iloc[0]

    assert pd.isna(athlete["athlete_id"])
    assert athlete["errormessage"] == "No reliable name match found"


def test_ambiguous_match(matched_data):
    # Multiple Olympedia candidates with the same name and year.
    unique_matches, all_athletes = matched_data

    assert 4 not in unique_matches["ID"].values

    athlete = all_athletes.loc[all_athletes["ID"] == 4].iloc[0]

    assert pd.isna(athlete["athlete_id"])
    assert athlete["errormessage"] == "Multiple name matches found"


def test_unmatched_athlete(matched_data):
    # Athletes without a matching name should remain in the output.
    unique_matches, all_athletes = matched_data

    assert 6 not in unique_matches["ID"].values

    athlete = all_athletes.loc[all_athletes["ID"] == 6].iloc[0]

    assert pd.isna(athlete["athlete_id"])
    assert athlete["errormessage"] == "No reliable name match found"


def test_all_athletes_preserved(test_data, matched_data):
    # Every original Kaggle athlete should appear exactly once.
    athletes, _, _ = test_data
    _, all_athletes = matched_data

    assert len(all_athletes) == athletes["ID"].nunique()
    assert all_athletes["ID"].is_unique
    assert set(all_athletes["ID"]) == set(athletes["ID"].unique())


def test_multiple_years_do_not_create_duplicates(matched_data):
    # An athlete participating in multiple years should match only once.
    unique_matches, all_athletes = matched_data

    assert len(unique_matches[unique_matches["ID"] == 1]) == 1
    assert len(all_athletes[all_athletes["ID"] == 1]) == 1


def test_unique_match_with_different_name(matched_data):
    # Different original names can match after normalization.
    unique_matches, _ = matched_data

    match = unique_matches.loc[unique_matches["ID"] == 1].iloc[0]

    assert match["Name"] == "Jos Garca"
    assert match["olympedia_name"] == "José García"


def test_no_false_match_from_same_name(matched_data):
    # Olympic years must overlap, even when names match.
    unique_matches, _ = matched_data

    # Anna Smith: same name, different year.
    assert 2 not in unique_matches["ID"].values

    # John Brown: same name, same year.
    assert 3 in unique_matches["ID"].values
