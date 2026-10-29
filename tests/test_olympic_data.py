import pandas as pd
import pytest

from olympic_data import OlympicData


@pytest.fixture
def sample_csv(tmp_path):
    data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie"],
        "Medal": ["Gold", "Silver", "Bronze", None],
    })

    filepath = tmp_path / "olympic_data.csv"
    data.to_csv(filepath, index=False)

    return filepath

def assert_prepared_data(olympic_data):
    expected_data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie"],
        "Bronze": [0, 0, 1, 0],
        "Silver": [0, 1, 0, 0],
        "Gold": [1, 0, 0, 0],
        "medals": [1, 1, 1, 0],
    }).astype({
        "Gold": "int32",
        "Silver": "int32",
        "Bronze": "int32",
        "medals": "int32",
    })

    pd.testing.assert_frame_equal(
        olympic_data.data,
        expected_data,
    )

def test_load_data(sample_csv):
    olympic_data = OlympicData(sample_csv)

    olympic_data.load_data()

    expected_data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie"],
        "Medal": ["Gold", "Silver", "Bronze", None],
    })

    pd.testing.assert_frame_equal(
        olympic_data.raw_data,
        expected_data,
    )

def test_prepare_data(sample_csv):
    olympic_data = OlympicData(sample_csv)
    olympic_data.load_data()

    original_data = olympic_data.raw_data.copy()

    olympic_data.prepare_data()

    assert_prepared_data(olympic_data)

    pd.testing.assert_frame_equal(
        olympic_data.raw_data,
        original_data,
    )
    
def test_load_and_prepare(sample_csv):
    olympic_data = OlympicData(sample_csv)

    olympic_data.load_and_prepare()

    assert olympic_data.raw_data is not None
    assert_prepared_data(olympic_data)
    
def test_prepare_data_without_loading():
    olympic_data = OlympicData("unused.csv")

    with pytest.raises(RuntimeError, match="Load the data first."):
        olympic_data.prepare_data()