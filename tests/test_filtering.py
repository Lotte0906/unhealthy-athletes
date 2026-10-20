import pandas as pd
import pytest

from filtering import (
    get_medal_winners,
    filter_by_year_range,
    get_first_n_names,
    filter_by_names,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie"],
        "Year": [1948, 1952, 1956, 1960],
        "Gold": [1, 0, 0, 0],
        "Silver": [0, 1, 0, 0],
        "Bronze": [0, 0, 1, 0],
    })


def test_get_medal_winners(sample_data):
    result = get_medal_winners(sample_data)

    assert len(result) == 3
    assert result["Name"].tolist() == ["Alice", "Bob", "Alice"]


def test_filter_by_year_range(sample_data):
    result = filter_by_year_range(sample_data, 1952, 1956)

    assert result["Year"].tolist() == [1952, 1956]


def test_filter_by_year_range_includes_endpoints(sample_data):
    result = filter_by_year_range(sample_data, 1948, 1960)

    assert result["Year"].tolist() == [1948, 1952, 1956, 1960]


def test_filter_by_year_range_invalid_range(sample_data):
    with pytest.raises(ValueError):
        filter_by_year_range(sample_data, 1960, 1948)


def test_get_first_n_names(sample_data):
    result = get_first_n_names(sample_data, n=2)

    assert result == ["Alice", "Bob"]


def test_filter_by_names(sample_data):
    result = filter_by_names(sample_data, ["Alice", "Charlie"])

    assert result["Name"].tolist() == ["Alice", "Alice", "Charlie"]


def test_filters_do_not_modify_original_data(sample_data):
    original = sample_data.copy()

    filter_by_year_range(sample_data, 1952, 1956)

    pd.testing.assert_frame_equal(sample_data, original)
