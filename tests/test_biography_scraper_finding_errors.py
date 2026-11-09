
import pytest
import requests

from biography_scraper_finding_errors import (
    attempt_find_wikidata_entry,
    find_wikidata_entry,
    get_wikidata_claims,
)


# --------------------------------------------------
# Fixtures
# --------------------------------------------------

@pytest.fixture
def sample_data():
    return [
        "Albert Einstein",
        "Alberb Einstein",
        "Keanu Reeves"
    ]


@pytest.fixture
def mock_wikidata_search(monkeypatch):
    """Simulate Wikidata search responses without internet requests."""

    def set_results(qids):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "search": [{"id": qid} for qid in qids]
                }

        def fake_get(url, params=None, headers=None, timeout=None):
            return FakeResponse()

        monkeypatch.setattr(
            "biography_scraper_finding_errors.requests.get",
            fake_get
        )

    return set_results


@pytest.fixture
def empty_person_entry():
    """Create a PersonEntry without Wikidata claims."""

    return {
        "name": "Albert Einstein",
        "qid": "Q937",
        "number_of_matches": 1,
        "matched_search_name": "Albert Einstein",
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": ""
    }


# --------------------------------------------------
# Tests for attempt_find_wikidata_entry()
# --------------------------------------------------

def test_search_no_results(mock_wikidata_search):
    mock_wikidata_search([])

    result = attempt_find_wikidata_entry("Unknown Athlete")

    assert result["qid"] is None
    assert result["number_of_matches"] == 0
    assert result["matched_search_name"] is None
    assert result["errormessage"] == ""


def test_search_one_result(mock_wikidata_search):
    mock_wikidata_search(["Q123"])

    result = attempt_find_wikidata_entry("Test Athlete")

    assert result["qid"] == "Q123"
    assert result["number_of_matches"] == 1
    assert result["matched_search_name"] == "Test Athlete"
    assert result["errormessage"] == ""


def test_search_multiple_results(mock_wikidata_search):
    mock_wikidata_search(["Q123", "Q456"])

    result = attempt_find_wikidata_entry("Test Athlete")

    assert result["qid"] == "Q123"
    assert result["number_of_matches"] == 2
    assert result["matched_search_name"] == "Test Athlete"
    assert result["errormessage"] == (
        "At least 2 Wikidata search results found"
    )


def test_search_fifty_results(mock_wikidata_search):
    qids = [f"Q{i}" for i in range(1, 51)]
    mock_wikidata_search(qids)

    result = attempt_find_wikidata_entry("Test Athlete")

    assert result["qid"] == "Q1"
    assert result["number_of_matches"] == 50
    assert result["errormessage"] == (
        "At least 50 Wikidata search results found"
    )


# --------------------------------------------------
# Tests for find_wikidata_entry()
# --------------------------------------------------

def test_find_wikidata_entry_preserves_existing_error(
    mock_wikidata_search
):
    mock_wikidata_search(["Q123", "Q456"])

    result = find_wikidata_entry(
        "Test Athlete",
        errormessage="No reliable name match found"
    )

    assert result["qid"] == "Q123"
    assert result["number_of_matches"] == 2
    assert result["errormessage"] == (
        "No reliable name match found | "
        "At least 2 Wikidata search results found"
    )


def test_find_wikidata_entry_no_results(mock_wikidata_search):
    mock_wikidata_search([])

    result = find_wikidata_entry("Unknown Athlete")

    assert result["qid"] is None
    assert result["errormessage"] == (
        "No Wikidata search results found for any name variation"
    )


# --------------------------------------------------
# Tests for get_wikidata_claims()
# --------------------------------------------------

def test_get_wikidata_claims_einstein(monkeypatch, empty_person_entry):

    def fake_get_entity_data(qid, headers=None):
        return {
            "entities": {
                "Q937": {
                    "claims": {
                        "P569": [{
                            "mainsnak": {
                                "datavalue": {
                                    "value": {
                                        "time": "+1879-03-14T00:00:00Z"
                                    }
                                }
                            }
                        }],
                        "P570": [{
                            "mainsnak": {
                                "datavalue": {
                                    "value": {
                                        "time": "+1955-04-18T00:00:00Z"
                                    }
                                }
                            }
                        }],
                        "P1196": [{
                            "mainsnak": {
                                "datavalue": {
                                    "value": {"id": "Q3739104"}
                                }
                            }
                        }]
                    }
                }
            }
        }

    def fake_get_label_from_qid(qid, headers=None):
        return "natural causes"

    monkeypatch.setattr(
        "biography_scraper_finding_errors.get_entity_data",
        fake_get_entity_data
    )
    monkeypatch.setattr(
        "biography_scraper_finding_errors.get_label_from_qid",
        fake_get_label_from_qid
    )

    result = get_wikidata_claims(empty_person_entry)

    assert result["birthdate"] == "+1879-03-14T00:00:00Z"
    assert result["deathdate"] == "+1955-04-18T00:00:00Z"
    assert result["status"] == "Dead"
    assert result["mannerofdeath"] == "natural causes"
    assert result["errormessage"] == ""


def test_get_wikidata_claims_without_qid():
    person_entry = {
        "name": "Unknown Athlete",
        "qid": None,
        "number_of_matches": 0,
        "matched_search_name": None,
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": "No Wikidata search results found"
    }

    result = get_wikidata_claims(person_entry)

    assert result["qid"] is None
    assert result["birthdate"] is None
    assert result["deathdate"] is None
    assert result["errormessage"] == (
        "No Wikidata search results found"
    )


def test_get_wikidata_claims_reeves(monkeypatch):
    person_entry = {
        "name": "Keanu Reeves",
        "qid": "Q43416",
        "number_of_matches": 1,
        "matched_search_name": "Keanu Reeves",
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": ""
    }

    def fake_get_entity_data(qid, headers=None):
        return {
            "entities": {
                "Q43416": {
                    "claims": {
                        "P569": [{
                            "mainsnak": {
                                "datavalue": {
                                    "value": {
                                        "time": "+1964-09-02T00:00:00Z"
                                    }
                                }
                            }
                        }]
                    }
                }
            }
        }

    def fake_check_if_alive_on_wikipedia(
        entity_data, headers=None
    ):
        return "Alive"

    monkeypatch.setattr(
        "biography_scraper_finding_errors.get_entity_data",
        fake_get_entity_data
    )
    monkeypatch.setattr(
        "biography_scraper_finding_errors.check_if_alive_on_wikipedia",
        fake_check_if_alive_on_wikipedia
    )

    result = get_wikidata_claims(person_entry)

    assert result["birthdate"] == "+1964-09-02T00:00:00Z"
    assert result["deathdate"] is None
    assert result["status"] == "Alive"
    assert result["mannerofdeath"] is None
    assert result["errormessage"] == ""
