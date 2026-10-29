
import pandas as pd
import pytest
from datetime import date

from processing import (
    convert_dict_to_pd_df,
    merge_dataframes,
    convert_dates,
    calculate_age_per_row,
    add_age,
)


@pytest.fixture
def sample_dicts():
    return [
        {"name": "Alice", "birthdate": "1990-05-10"},
        {"name": "Bob", "birthdate": "1985-08-20"},
    ]


@pytest.fixture
def olympic_data():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie"],
        "Year": [1948, 1952, 1956, 1960],
    })


@pytest.fixture
def biography_data():
    return pd.DataFrame({
        "name": ["Alice", "Bob"],
        "birthdate": [date(1930, 1, 1), date(1925, 2, 2)],
    })


@pytest.fixture
def date_data():
    return pd.DataFrame({
        "birthdate": [
            "+1990-05-10T00:00:00Z",
            "+1985-08-20T00:00:00Z",
        ],
        "deathdate": [
            "+2020-06-15T00:00:00Z",
            None,
        ],
    })


@pytest.fixture
def age_data():
    return pd.DataFrame({
        "birthdate": [
            date(1950, 6, 15),
            date(2000, 6, 15),
            None,
        ],
        "deathdate": [
            date(2020, 6, 14),
            None,
            date(2020, 1, 1),
        ],
    })


def test_convert_dict_to_pd_df(sample_dicts):
    result = convert_dict_to_pd_df(sample_dicts)

    expected = pd.DataFrame(sample_dicts)

    pd.testing.assert_frame_equal(result, expected)


def test_convert_dict_to_pd_df_empty():
    result = convert_dict_to_pd_df([])

    assert result.empty


def test_merge_dataframes(olympic_data, biography_data):
    result = merge_dataframes(olympic_data, biography_data)

    expected = pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie"],
        "Year": [1948, 1952, 1956, 1960],
        "birthdate": [
            date(1930, 1, 1),
            date(1925, 2, 2),
            date(1930, 1, 1),
            None,
        ],
    })

    pd.testing.assert_frame_equal(result, expected)


def test_convert_dates(date_data):
    result = convert_dates(date_data)

    assert result["birthdate"].tolist() == [
        date(1990, 5, 10),
        date(1985, 8, 20),
    ]
    assert result["deathdate"].iloc[0] == date(2020, 6, 15)
    assert pd.isna(result["deathdate"].iloc[1])


def test_calculate_age_per_row_deceased():
    row = pd.Series({
        "birthdate": date(1950, 6, 15),
        "deathdate": date(2020, 6, 14),
    })

    result = calculate_age_per_row(row, date(2026, 1, 1))

    assert result == 69


def test_calculate_age_per_row_alive():
    row = pd.Series({
        "birthdate": date(2000, 6, 15),
        "deathdate": None,
    })

    result = calculate_age_per_row(row, date(2026, 6, 14))

    assert result == 25


def test_calculate_age_per_row_missing_birthdate():
    row = pd.Series({
        "birthdate": None,
        "deathdate": date(2020, 6, 15),
    })

    result = calculate_age_per_row(row, date(2026, 1, 1))

    assert result is None


def test_add_age(age_data):
    currentdate = date(2026, 6, 14)

    result = add_age(age_data, currentdate)

    assert result["age"].tolist() == [69, 25, pd.NA]
    assert str(result["age"].dtype) == "Int64"
