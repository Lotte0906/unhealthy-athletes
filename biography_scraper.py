# documentation used:
# https://www.mediawiki.org/wiki/Wikibase/API
# https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge
# https://www.mediawiki.org/wiki/API:Query
# https://www.wikidata.org/wiki/Special:ApiSandbox

import requests
from typing import TypedDict

class PersonEntry(TypedDict):
    name: str
    qid: str | None
    birthdate: str | None
    deathdate: str | None
    status: str | None
    mannerofdeath: str | None
    errormessage: str | None

# SYSTEM HYGIENE HEADERS: Explicitly identifying our scraper to avoid server drop rules
HEADERS = {
        "User-Agent": "ResearchDataExtractionTool/3.0 (lottee0906@gmail.com) Python-requests/2.31.0",
        "Accept": "application/json"}

def find_wikidata_entry(person_name, headers=HEADERS):
    base_url = "https://www.wikidata.org/w/api.php"
    person_entry = {"name": person_name,
                   "qid" : None,
                   "birthdate" : None,
                   "deathdate" : None,
                   "status" : None,
                   "mannerofdeath" : None,
                   "errormessage" : None
                  }
        
    # SEARCH FOR THE PERSON TO GET THE QID
    search_params = {
        "action": "wbsearchentities",
        "search": person_name,
        "language": "en",
        "format": "json",
        "formatversion": "2"
    }
    
    try:
        response = requests.get(base_url, params=search_params, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Guard clause: catching raw HTML block pages before they hit the json decoder
        if "text/html" in response.headers.get("Content-Type", ""):
            person_entry["errormessage"] = "Technical Error"
            return person_entry
            
        search_response = response.json()
    except: # TODO: catch specific errors
        person_entry["errormessage"] = "Technical Error"
        return person_entry
    
    search_results = search_response.get("search")
    if not search_results:
        person_entry["errormessage"] = f"No results found for {person_name}."
        return person_entry
    
    # Safely isolate the premier matching entity block
    best_match = search_results[0]     # TODO: check if the first match is the right one and find a solution.
    person_entry["qid"] = best_match["id"]
    return person_entry

def get_entity_data(qid, headers=HEADERS):
    """Takes a Wikidata QID and fetches the raw entity data package
    containing both claims and sitelinks.
    """
        
    base_url = "https://wikidata.org/w/api.php"
    entity_params = {
        "action": "wbgetentities",
        "ids": qid,
        "languages": "en",
        "props": "claims|sitelinks",
        "format": "json",
        "formatversion": "2"
    }
    
    try:
        response = requests.get(base_url, params=entity_params, headers=headers, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        
        return raw_data
    except Exception:
        return None

def check_if_alive_on_wikipedia(entity_data, headers = HEADERS):
    """helper function that checks if the person is alive"""
    wp_api_url = "https://en.wikipedia.org/w/api.php"
    qid = entity_data.get('qid')
    sitelinks = entity_data['entities'][qid].get("sitelinks", {})

    if "enwiki" in sitelinks:
        wp_title = sitelinks["enwiki"]["title"]  
    else:
        wp_title = None
    
    wp_params = {
        "action": "query",
        "titles": wp_title,
        "prop": "categories",
        "clcategories": "Category:Living people",
        "format": "json"
    }
    try:
        response = requests.get(wp_api_url, params=wp_params, headers=headers, timeout=10)
        response.raise_for_status()
        wp_data = response.json()
        pages = wp_data.get("query", {}).get("pages", {})
        page_values= list(pages.values())[0]
        if "categories" in page_values:
            return "Alive"
        return None
    except Exception:
        return None
    
def get_label_from_qid(qid, headers=HEADERS):
    """Takes a Wikidata QID (e.g., Q2256736) and fetches its English text label."""
    if not qid or not str(qid).startswith("Q"):
        return None
    
    base_url = "https://www.wikidata.org/w/api.php"
      
    label_params = {
        "action": "wbgetentities",
        "ids": qid,
        "languages": "en",
        "props": "labels",
        "format": "json",
        "formatversion": "2"
    }
    
    try:
        response = requests.get(base_url, params=label_params, headers=headers, timeout=10)
        response.raise_for_status()
        label_data = response.json()
        
        label = label_data["entities"][qid]["labels"]["en"]["value"]
        return label
    except Exception:
        return None
    
def get_wikidata_claims(person_entry: PersonEntry, headers=HEADERS) -> PersonEntry:
    """"extracts date of birth, date of death, status and manner of death from wikidata using the persons QID"""
    if person_entry['qid'] == None:
        return person_entry
    raw_data = get_entity_data(person_entry['qid'], headers=headers)
    claims = raw_data["entities"][person_entry['qid']]["claims"]
    base_url = "https://www.wikidata.org/w/api.php"
    if claims == {}:
        person_entry["birthdate"] = None
        person_entry["deathdate"] = None
        person_entry["mannerofdeath"] = None
        person_entry["status"] = None
        return (person_entry)
    
    # Extract Birthdate (Property P569)
    try:
        person_entry["birthdate"] = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
    except (KeyError, IndexError):
        person_entry["birthdate"] = None

    # Extract Deathdate (Property P570)
    try:
        person_entry["deathdate"] = claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"]
        person_entry["status"] = "Dead"
    except (KeyError, IndexError):
        person_entry["deathdate"] = None
        raw_data['qid'] = person_entry['qid']
        entity_data = raw_data
        person_entry["status"] = check_if_alive_on_wikipedia(entity_data,
                                                             headers = headers)

    # Extract manner/cause of death (Property P1196/P509)
    if person_entry["status"] == "Dead":
        try:
            manner_qid = claims["P1196"][0]["mainsnak"]["datavalue"]["value"]["id"]
            person_entry["mannerofdeath"] = get_label_from_qid(manner_qid, headers)
        except (KeyError, IndexError):
            try:
                manner_qid = claims["P509"][0]["mainsnak"]["datavalue"]["value"]["id"]
                person_entry["mannerofdeath"] = get_label_from_qid(manner_qid, headers)
            except:
                person_entry["mannerofdeath"] = None       
    else:
        person_entry["mannerofdeath"] = None   
    return (person_entry)