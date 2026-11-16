import datetime
import json

import pandas as pd
import pytest

from unhealthy_athletes.workflow import (
    process_batch,
    run_scraping,
    REQUIRED_BATCH_COLUMNS,
)


REFERENCE_DATE = datetime.date(2026, 1, 1)


# --------------------------------------------------
# Fixtures for process_batch()
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

    return olympic_data, batch_athletes, REFERENCE_DATE


@pytest.fixture
def mock_wikidata(monkeypatch):
    """Replace Wikidata functions with artificial results."""

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

    monkeypatch.setattr(
        "unhealthy_athletes.workflow.find_wikidata_entry",
        fake_find_wikidata_entry,
    )

    monkeypatch.setattr(
        "unhealthy_athletes.workflow.get_wikidata_claims",
        lambda entry: entry,
    )

    return searched_names


@pytest.fixture
def processed_data(test_data, mock_wikidata):
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
    assert set(processed_data["ID"]) == {1, 2, 3}
    assert len(processed_data) == 4


def test_correct_search_names_used(processed_data, mock_wikidata):
    assert mock_wikidata == [
        "José García",
        "Anna Smith",
        "John Brown",
    ]


def test_existing_errors_preserved(processed_data):
    anna = processed_data.loc[
        processed_data["ID"] == 2
    ].iloc[0]

    john = processed_data.loc[
        processed_data["ID"] == 3
    ].iloc[0]

    assert "No reliable name match found" in anna["errormessage"]
    assert "Multiple name matches found" in john["errormessage"]


def test_new_errors_appended(processed_data):
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
    jose = processed_data.loc[
        processed_data["ID"] == 1
    ]

    assert len(jose) == 2
    assert (jose["qid"] == "Q101").all()


def test_age_calculated_correctly(processed_data):
    jose = processed_data.loc[
        processed_data["ID"] == 1
    ].iloc[0]

    assert jose["age"] == 40

    anna = processed_data.loc[
        processed_data["ID"] == 2
    ].iloc[0]

    assert anna["age"] == 36


def test_missing_wikidata_information(processed_data):
    john = processed_data.loc[
        processed_data["ID"] == 3
    ].iloc[0]

    assert pd.isna(john["qid"])
    assert pd.isna(john["birthdate"])
    assert pd.isna(john["age"])


def test_no_duplicate_rows_created(processed_data, test_data):
    olympic_data, batch_athletes, _ = test_data

    expected_rows = olympic_data[
        olympic_data["ID"].isin(batch_athletes["ID"])
    ]

    assert len(processed_data) == len(expected_rows)


# --------------------------------------------------
# Fixtures for run_scraping()
# --------------------------------------------------

@pytest.fixture
def scraping_data():
    """Small dataset with four athletes."""

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
    """Replace scraping with a predictable fake implementation."""

    processed_batches = []

    def fake_process_batch(olympic_data, batch_athletes, currentdate):
        ids = batch_athletes["ID"].tolist()
        processed_batches.append(ids)

        data = {
            column: [None] * len(ids)
            for column in REQUIRED_BATCH_COLUMNS
        }

        data["ID"] = ids
        data["qid"] = [f"Q{i}" for i in ids]
        data["birthdate"] = ["1990-01-01"] * len(ids)
        data["deathdate"] = [None] * len(ids)
        data["status"] = ["Alive"] * len(ids)
        data["age"] = [36] * len(ids)
        data["errormessage"] = [""] * len(ids)
        data["birthdate_original"] = ["1990-01-01"] * len(ids)

        return pd.DataFrame(data)

    monkeypatch.setattr(
        "unhealthy_athletes.workflow.process_batch",
        fake_process_batch,
    )

    return processed_batches


@pytest.fixture
def scraping_environment(
    tmp_path, monkeypatch, scraping_data, mock_process_batch
):
    """Use an isolated directory for every test."""
    monkeypatch.chdir(tmp_path)

    output_dir = tmp_path / "data"
    output_dir.mkdir()

    olympic_data, all_athletes = scraping_data

    return {
        "olympic_data": olympic_data,
        "all_athletes": all_athletes,
        "processed_batches": mock_process_batch,
        "output_dir": output_dir,
    }


def run_test_scraping(env, **kwargs):
    """Run scraping with a fixed date and isolated output directory."""
    return run_scraping(
        env["olympic_data"],
        env["all_athletes"],
        n_batches=2,
        reference_date=REFERENCE_DATE,
        output_dir=env["output_dir"],
        **kwargs,
    )


# --------------------------------------------------
# Tests for saving and resuming
# --------------------------------------------------

def test_run_scraping_saves_batches(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)

    assert env["processed_batches"] == [[1, 2], [3, 4]]

    for batch_number in (1, 2):
        csv_file = env["output_dir"] / (
            f"entries{batch_number}of2.csv"
        )
        metadata_file = csv_file.with_suffix(".json")

        assert csv_file.exists()
        assert metadata_file.exists()

        assert not csv_file.with_suffix(".tmp").exists()
        assert not metadata_file.with_suffix(".tmp").exists()

        result = pd.read_csv(csv_file)

        assert REQUIRED_BATCH_COLUMNS.issubset(result.columns)

        with metadata_file.open(encoding="utf-8") as file:
            metadata = json.load(file)

        assert metadata["batch_number"] == batch_number
        assert metadata["n_batches"] == 2
        assert metadata["reference_date"] == "2026-01-01"
        assert metadata["provenance_verified"] is True
        assert metadata["legacy_adopted"] is False
        assert len(metadata["output_hash"]) == 64
        assert len(metadata["input_fingerprint"]) == 64


def test_run_scraping_skips_completed_batches(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)

    env["processed_batches"].clear()

    run_test_scraping(env)

    # No scraping should happen during the second run.
    assert env["processed_batches"] == []


def test_run_scraping_reprocesses_incomplete_batch(
    scraping_environment
):
    env = scraping_environment

    temporary_file = env["output_dir"] / "entries1of2.tmp"
    temporary_file.write_text("incomplete data")

    run_test_scraping(env)

    assert env["processed_batches"] == [[1, 2], [3, 4]]
    assert not temporary_file.exists()

    result = pd.read_csv(
        env["output_dir"] / "entries1of2.csv"
    )

    assert result["ID"].tolist() == [1, 2]
    assert result["qid"].tolist() == ["Q1", "Q2"]


# --------------------------------------------------
# Tests for metadata validation
# --------------------------------------------------

def test_changed_reference_date_rejected(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    with pytest.raises(ValueError, match="reference_date"):
        run_scraping(
            env["olympic_data"],
            env["all_athletes"],
            n_batches=2,
            reference_date=datetime.date(2027, 1, 1),
            output_dir=env["output_dir"],
        )

    assert env["processed_batches"] == []


def test_changed_input_rejected(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    changed_athletes = env["all_athletes"].copy()
    changed_athletes.loc[0, "search_name"] = "Different Name"

    with pytest.raises(ValueError, match="input_fingerprint"):
        run_scraping(
            env["olympic_data"],
            changed_athletes,
            n_batches=2,
            reference_date=REFERENCE_DATE,
            output_dir=env["output_dir"],
        )

    assert env["processed_batches"] == []


def test_changed_processing_version_rejected(
    scraping_environment, monkeypatch
):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    monkeypatch.setattr(
        "unhealthy_athletes.workflow.PROCESSING_VERSION",
        999,
    )

    with pytest.raises(ValueError, match="processing_version"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


def test_modified_csv_rejected(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    csv_file = env["output_dir"] / "entries1of2.csv"

    # Modify a valid CSV without changing its columns or IDs.
    df = pd.read_csv(csv_file)
    df.loc[0, "qid"] = "Q999"
    df.to_csv(csv_file, index=False)

    with pytest.raises(ValueError, match="CSV changed"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


def test_missing_metadata_rejected(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    metadata_file = env["output_dir"] / "entries1of2.json"
    metadata_file.unlink()

    with pytest.raises(ValueError, match="no metadata"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


def test_missing_csv_with_metadata_rejected(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    csv_file = env["output_dir"] / "entries1of2.csv"
    csv_file.unlink()

    with pytest.raises(ValueError, match="CSV is missing"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


# --------------------------------------------------
# Tests for CSV validation
# --------------------------------------------------

def test_missing_columns_rejected(scraping_environment):
    env = scraping_environment

    csv_file = env["output_dir"] / "entries1of2.csv"
    csv_file.write_text("ID,qid\n1,Q1\n2,Q2\n")

    with pytest.raises(ValueError, match="missing columns"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


def test_wrong_athlete_ids_rejected(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    csv_file = env["output_dir"] / "entries1of2.csv"

    df = pd.read_csv(csv_file)
    df.loc[0, "ID"] = 999
    df.to_csv(csv_file, index=False)

    with pytest.raises(ValueError, match="expected athlete rows"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


# --------------------------------------------------
# Tests for legacy batches
# --------------------------------------------------

def test_legacy_batch_requires_permission(scraping_environment):
    env = scraping_environment

    run_test_scraping(env)
    env["processed_batches"].clear()

    metadata_file = env["output_dir"] / "entries1of2.json"
    metadata_file.unlink()

    with pytest.raises(ValueError, match="no metadata"):
        run_test_scraping(env)

    assert env["processed_batches"] == []


def test_legacy_batch_can_be_adopted(scraping_environment):
    env = scraping_environment

    # First generate a structurally valid CSV.
    run_test_scraping(env)

    metadata_file = env["output_dir"] / "entries1of2.json"
    metadata_file.unlink()

    env["processed_batches"].clear()

    run_test_scraping(env, adopt_legacy=True)

    # Both CSV files already exist, so no scraping is needed.
    assert env["processed_batches"] == []

    assert metadata_file.exists()

    with metadata_file.open(encoding="utf-8") as file:
        metadata = json.load(file)

    assert metadata["legacy_adopted"] is True
    assert metadata["provenance_verified"] is False


def test_invalid_legacy_batch_not_adopted(scraping_environment):
    env = scraping_environment

    csv_file = env["output_dir"] / "entries1of2.csv"
    csv_file.write_text("ID,qid\n1,Q1\n2,Q2\n")

    with pytest.raises(ValueError, match="missing columns"):
        run_test_scraping(env, adopt_legacy=True)

    assert not csv_file.with_suffix(".json").exists()
    assert env["processed_batches"] == []
