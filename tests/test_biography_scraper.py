import pandas as pd
import requests
import pytest

from biography_scraper import (find_wikidata_entry,
                               get_entity_data,
                               check_if_alive_on_wikipedia,
                               get_label_from_qid,
                               get_wikidata_claims)


@pytest.fixture
def sample_data():
    return ['Albert Einstein', # dead person
            'Alberb Einstein', # wrong name
            'Keanu Reeves'] # alive person
   
    
def test_find_wikidata_entry(sample_data):

    assert find_wikidata_entry(sample_data[0]) == {'name': 'Albert Einstein',
                                                   'qid': 'Q937',
                                                   'birthdate': None,
                                                   'deathdate': None,
                                                   'status': None,
                                                   'mannerofdeath': None,
                                                   'errormessage': ""
                                                  }

    assert find_wikidata_entry(sample_data[1]) == {'name': 'Alberb Einstein',
                                                   'qid': None,
                                                   'birthdate': None,
                                                   'deathdate': None,
                                                   'status': None,
                                                   'mannerofdeath': None,
                                                   'errormessage': 'No results found for Alberb Einstein. '
                                                  }
    
    assert find_wikidata_entry(sample_data[2]) == {'name': 'Keanu Reeves',
                                                   'qid': 'Q43416',
                                                   'birthdate': None,
                                                   'deathdate': None,
                                                   'status': None,
                                                   'mannerofdeath': None,
                                                   'errormessage': ""
                                                  }


def test_get_wikidata_claims_einstein(monkeypatch):
    def fake_get_entity_data(qid, headers=None):
        return {
            "entities": {"Q937": {"claims":{
                "P569": [{"mainsnak": {"datavalue": {"value": {"time": "+1879-03-14T00:00:00Z"}}}}],
                "P570": [{"mainsnak": {"datavalue": {"value": {"time": "+1955-04-18T00:00:00Z"}}}}],
                "P1196": [{"mainsnak": {"datavalue": {"value": {"id": "Q3739104"}}}}]
                                  }}}}

    def fake_get_label_from_qid(qid, headers=None):
        return "natural causes"

    monkeypatch.setattr(
        "biography_scraper.get_entity_data",
        fake_get_entity_data
    )
    monkeypatch.setattr(
        "biography_scraper.get_label_from_qid",
        fake_get_label_from_qid
    )

    person_entry = {
        "name": "Albert Einstein",
        "qid": "Q937",
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": ""
    }

    assert get_wikidata_claims(person_entry) == {
        "name": "Albert Einstein",
        "qid": "Q937",
        "birthdate": "+1879-03-14T00:00:00Z",
        "deathdate": "+1955-04-18T00:00:00Z",
        "status": "Dead",
        "mannerofdeath": "natural causes",
        "errormessage": ""
    }    
    
def test_get_wikidata_claims_alberb():
    person_entry ={
        'name': 'Alberb Einstein',
        'qid': None,
        'birthdate': None,
        'deathdate': None,
        'status': None,
        'mannerofdeath': None,
        'errormessage': 'No results found for Alberb Einstein. '
        }

    assert get_wikidata_claims(person_entry) == {
        'name': 'Alberb Einstein',
        'qid': None,
        'birthdate': None,
        'deathdate': None,
        'status': None,
        'mannerofdeath': None,
        'errormessage': 'No results found for Alberb Einstein. '
       }
    
def test_get_wikidata_claims_Reeves(monkeypatch):
    def fake_get_entity_data(qid, headers=None):
        return {
            "entities": {"Q43416": {"claims":{
                "P569": [{"mainsnak": {"datavalue": {"value": {"time": "+1964-09-02T00:00:00Z"}}}}]
            }}}}

    def fake_check_if_alive_on_wikipedia(entity_data, headers=None):
        return "Alive"

    monkeypatch.setattr(
        "biography_scraper.get_entity_data",
        fake_get_entity_data
    )
    monkeypatch.setattr(
        "biography_scraper.check_if_alive_on_wikipedia",
        fake_check_if_alive_on_wikipedia
    )

    person_entry = {
        "name": "Keanu Reeves",
        "qid": "Q43416",
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": ""
    }

    assert get_wikidata_claims(person_entry) == {
        'name': 'Keanu Reeves',
        'qid': 'Q43416',
        'birthdate': '+1964-09-02T00:00:00Z',
        'deathdate': None,
        'status': 'Alive',
        'mannerofdeath': None,
        'errormessage': ""}
    
# integration tests    
def test_get_wikidata_claims(sample_data):
    assert get_wikidata_claims(find_wikidata_entry(sample_data[0])) == {'name': 'Albert Einstein',
                                                                        'qid': 'Q937',
                                                                        'birthdate': '+1879-03-14T00:00:00Z',
                                                                        'deathdate': '+1955-04-18T00:00:00Z',
                                                                        'status': 'Dead',
                                                                        'mannerofdeath': 'natural causes',
                                                                        'errormessage': ""
                                                                       }
    
    assert get_wikidata_claims(find_wikidata_entry(sample_data[1])) == {'name': 'Alberb Einstein',
                                                                        'qid': None,
                                                                        'birthdate': None,
                                                                        'deathdate': None,
                                                                        'status': None,
                                                                        'mannerofdeath': None,
                                                                        'errormessage': 'No results found for Alberb Einstein. '
                                                                       }
    
    assert get_wikidata_claims(find_wikidata_entry(sample_data[2])) == {'name': 'Keanu Reeves',
                                                                        'qid': 'Q43416',
                                                                        'birthdate': '+1964-09-02T00:00:00Z',
                                                                        'deathdate': None,
                                                                        'status': 'Alive',
                                                                        'mannerofdeath': None,
                                                                        'errormessage': ""}