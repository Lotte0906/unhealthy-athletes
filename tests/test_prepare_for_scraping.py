import pandas as pd
import pytest

from prepare_for_scraping import (
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

def test_get_first_n_names(sample_data):
    result = get_first_n_names(sample_data, n=2)

    assert result == ["Alice", "Bob"]

    
def test_get_first_n_names_negative(sample_data):
    with pytest.raises(ValueError, match="n must be non-negative."):
        get_first_n_names(sample_data, n=-1)    
    
    
def test_get_first_0_names(sample_data):
    result = get_first_n_names(sample_data, n=0)

    assert result == []    
    

def test_filter_by_names_as_list(sample_data):
    result = filter_by_names(sample_data, ["Alice", "Charlie"])

    assert result["Name"].tolist() == ["Alice", "Alice", "Charlie"]
    
def test_filter_by_names_as_list_no_matches(sample_data):
    result = filter_by_names(sample_data, ["Nobody"])

    assert result.empty
    
def test_filter_by_names_as_number(sample_data):
    result = filter_by_names(sample_data, 2)

    assert result["Name"].tolist() == ["Alice", "Bob", "Alice"]