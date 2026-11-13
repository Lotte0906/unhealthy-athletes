
import datetime

import pandas as pd
import pytest

from workflow import process_batch, run_scraping


# --------------------------------------------------
# Fixtures
# --------------------------------------------------

@pytest.fixture
def test_data():
    """Create artificial Olympic data and a batch of athletes."""

    olympic_data = pd.DataFrame({
        "ID": [1, 1, 2, 3, 4],
        "Name": [
            "Jos Garca",
            "Jos Garca",
            "Anna Smith",
            "John Brown",
            "Jane Doe",
        ],
        "Year": [2000, 2004, 2008, 2012, 1996],
        "search_name": [
            "José García",
            "José García",
            "Anna Smith",
            "John Brown",
            "Jane Doe",
        ],
        "errormessage": [
            None,
            None,
            "No reliable name match found",
            "Multiple name matches found",
            None,
        ],
    })

    batch_athletes = pd.DataFrame({
        "ID": [1, 2, 3],
        "search_name": [
            "José García",
            "Anna Smith",
            "John Brown",
        ],
        "errormessage": [
            None,
            "No reliable name match found",
            "Multiple name matches found",
        ],
    })

    currentdate = datetime.date(2026, 1, 1)

    return olympic_data, batch_athletes, currentdate


@pytest.fixture
def mock_wikidata(monkeypatch):
    """Replace Wikidata functions with predictable artificial results."""

    searched_names = []

    def fake_find_wikidata_entry(name, errormessage=""):
        searched_names.append(name)

        entries = {
            "José García": {
                "qid": "Q101",
                "birthdate": "1980-01-01",
                "deathdate": "2020-01-01",
                "status": "Dead",
                "new_error": None,
            },
            "Anna Smith": {
                "qid": "Q102",
                "birthdate": "1990-01-01",
                "deathdate": None,
                "status": "Alive",
                "new_error": "Wikidata warning",
            },
            "John Brown": {
                "qid": None,
                "birthdate": None,
                "deathdate": None,
                "status": None,
                "new_error": "No Wikidata search results found",
            },
        }

        data = entries[name]
        errors = errormessage

        if data["new_error"]:
            if errors:
                errors += " | "
            errors += data["new_error"]

        return {
            "name": name,
            "qid": data["qid"],
            "birthdate": data["birthdate"],
            "deathdate": data["deathdate"],
            "status": data["status"],
            "errormessage": errors,
        }

    def fake_get_wikidata_claims(person_entry):
        return person_entry

    monkeypatch.setattr(
        "workflow.find_wikidata_entry",
        fake_find_wikidata_entry,
    )

    monkeypatch.setattr(
        "workflow.get_wikidata_claims",
        fake_get_wikidata_claims,
    )

    return searched_names


@pytest.fixture
def processed_data(test_data, mock_wikidata):
    """Process the artificial batch without contacting Wikidata."""

    olympic_data, batch_athletes, currentdate = test_data

    return process_batch(
        olympic_data,
        batch_athletes,
        currentdate,
    )


# --------------------------------------------------
# Tests for process_batch()
# --------------------------------------------------

def test_only_selected_athletes_processed(processed_data):
    # Athlete 4 is not in the selected batch.
    assert set(processed_data["ID"]) == {1, 2, 3}
    assert len(processed_data) == 4


def test_correct_search_names_used(processed_data, mock_wikidata):
    # Olympedia's corrected name should be used for athlete 1.
    assert mock_wikidata == [
        "José García",
        "Anna Smith",
        "John Brown",
    ]


def test_existing_errors_preserved(processed_data):
    # Existing matching errors should survive Wikidata processing.
    anna = processed_data.loc[
        processed_data["ID"] == 2
    ].iloc[0]

    john = processed_data.loc[
        processed_data["ID"] == 3
    ].iloc[0]

    assert "No reliable name match found" in anna["errormessage"]
    assert "Multiple name matches found" in john["errormessage"]


def test_new_errors_appended(processed_data):
    # New Wikidata errors should be appended, not overwrite old ones.
    anna = processed_data.loc[
        processed_data["ID"] == 2
    ].iloc[0]

    john = processed_data.loc[
        processed_data["ID"] == 3
    ].iloc[0]

    assert anna["errormessage"] == (
        "No reliable name match found | Wikidata warning"
    )

    assert john["errormessage"] == (
        "Multiple name matches found | "
        "No Wikidata search results found"
    )


def test_merge_uses_athlete_id(processed_data):
    # Wikidata results should be associated with the correct Kaggle ID.
    jose = processed_data.loc[
        processed_data["ID"] == 1
    ]

    assert len(jose) == 2
    assert (jose["qid"] == "Q101").all()


def test_age_calculated_correctly(processed_data):
    # Age at death for José García: exactly 40 years.
    jose = processed_data.loc[
        processed_data["ID"] == 1
    ].iloc[0]

    assert jose["age"] == 40

    # Anna Smith is alive on the artificial current date.
    anna = processed_data.loc[
        processed_data["ID"] == 2
    ].iloc[0]

    assert anna["age"] == 36


def test_missing_wikidata_information(processed_data):
    # An athlete without Wikidata results must remain in the output.
    john = processed_data.loc[
        processed_data["ID"] == 3
    ].iloc[0]

    assert pd.isna(john["qid"])
    assert pd.isna(john["birthdate"])
    assert pd.isna(john["age"])


def test_no_duplicate_rows_created(processed_data, test_data):
    # Processing should preserve the original Olympic event rows.
    olympic_data, batch_athletes, _ = test_data

    expected_rows = olympic_data[
        olympic_data["ID"].isin(batch_athletes["ID"])
    ]

    assert len(processed_data) == len(expected_rows)


# --------------------------------------------------
# Tests for run_scraping()
# --------------------------------------------------

@pytest.fixture
def scraping_data():
    """Small dataset containing four athletes."""

    all_athletes = pd.DataFrame({
        "ID": [1, 2, 3, 4],
        "search_name": [
            "Athlete A",
            "Athlete B",
            "Athlete C",
            "Athlete D",
        ],
    })

    olympic_data = pd.DataFrame({
        "ID": [1, 2, 3, 4],
        "Name": [
            "Athlete A",
            "Athlete B",
            "Athlete C",
            "Athlete D",
        ],
    })

    return olympic_data, all_athletes


@pytest.fixture
def mock_process_batch(monkeypatch):
    """Replace process_batch with a fake function."""

    processed_batches = []

    def fake_process_batch(olympic_data, batch_athletes, currentdate):
        processed_batches.append(batch_athletes["ID"].tolist())

        return pd.DataFrame({
            "ID": batch_athletes["ID"].tolist(),
            "qid": [
                f"Q{i}" for i in batch_athletes["ID"]
            ],
        })

    monkeypatch.setattr(
        "workflow.process_batch",
        fake_process_batch,
    )

    return processed_batches


def test_run_scraping_saves_batches(
    tmp_path, monkeypatch, scraping_data, mock_process_batch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()

    olympic_data, all_athletes = scraping_data

    run_scraping(
        olympic_data,
        all_athletes,
        n_batches=2,
    )

    assert mock_process_batch == [[1, 2], [3, 4]]

    assert (tmp_path / "data/entries1of2.csv").exists()
    assert (tmp_path / "data/entries2of2.csv").exists()

    assert not (tmp_path / "data/entries1of2.tmp").exists()
    assert not (tmp_path / "data/entries2of2.tmp").exists()


def test_run_scraping_skips_completed_batches(
    tmp_path, monkeypatch, scraping_data, mock_process_batch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()

    # Pretend that the first batch was already completed.
    (tmp_path / "data/entries1of2.csv").write_text(
        "ID,qid\n1,Q1\n2,Q2\n"
    )

    olympic_data, all_athletes = scraping_data

    run_scraping(
        olympic_data,
        all_athletes,
        n_batches=2,
    )

    # Only the second batch should be processed.
    assert mock_process_batch == [[3, 4]]

    assert (tmp_path / "data/entries1of2.csv").exists()
    assert (tmp_path / "data/entries2of2.csv").exists()


def test_run_scraping_reprocesses_incomplete_batch(
    tmp_path, monkeypatch, scraping_data, mock_process_batch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()

    # Simulate an interrupted save of the first batch.
    (tmp_path / "data/entries1of2.tmp").write_text(
        "incomplete data"
    )

    olympic_data, all_athletes = scraping_data

    run_scraping(
        olympic_data,
        all_athletes,
        n_batches=2,
    )

    # Both batches should be processed.
    assert mock_process_batch == [[1, 2], [3, 4]]

    # The incomplete temporary file should be replaced.
    assert (tmp_path / "data/entries1of2.csv").exists()
    assert not (tmp_path / "data/entries1of2.tmp").exists()

    result = pd.read_csv(
        tmp_path / "data/entries1of2.csv"
    )

    assert result["ID"].tolist() == [1, 2]
    assert result["qid"].tolist() == ["Q1", "Q2"]
