import requests

search_person() — find possible Wikidata entities.
get_entity_claims() — retrieve the claims for a chosen entity.
extract_date() — extract a date from a claim.
get_person_dates() — coordinate the process and return the result.

def get_person_dates(person_name):


from typing import TypedDict


class PersonEntry(TypedDict):
    name: str
    qid: str | None
    birthdate: str | None
    deathdate: str | None
    errormessage: str | None

    
def find_wikidata_entry(person_name):
    base_url = "https://www.wikidata.org/w/api.php"
    
    # SYSTEM HYGIENE HEADERS: Explicitly identifying our scraper to avoid server drop rules
    headers = {
        "User-Agent": "ResearchDataExtractionTool/3.0 (lottee0906@gmail.com) Python-requests/2.31.0",
        "Accept": "application/json"
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
            return {
            "name": person_name,
            "qid": None,
            "birthdate": None,
            "deathdate": None,
            "errormessage": f"Technical Error"
            }
            
        search_response = response.json()
    except:
        return {
            "name": person_name,
            "qid": None,
            "birthdate": None,
            "deathdate": None,
            "errormessage": f"Technical Error"
        }
    
    search_results = search_response.get("search")
    if not search_results:
        return {
            "name": person_name,
            "qid": None,
            "birthdate": None,
            "deathdate": None,
            "errormessage": f"No results found for {person_name}."
        }
    
    # Safely isolate the premier matching entity block
    best_match = search_results[0]     # TODO: check if the first match is the right one and find a solution.
    qid = best_match["id"]
    return {
            "name": person_name,
            "qid": qid,
            "birthdate": None,
            "deathdate": None,
            "errormessage": None
    }
    
def get_wikidata_claims(person_entry: PersonEntry) -> PersonEntry:
    # FETCH CLAIMS USING THE API ---
    entity_params = {
        "action": "wbgetentities",
        "ids": qid,
        "languages": "en",
        "props": "claims",  
        "format": "json",
        "formatversion": "2"
    }
    
    try:
        entity_response = requests.get(base_url, params=entity_params, headers=headers)
        entity_response.raise_for_status()
        entity_data = entity_response.json()
        
        claims = entity_data["entities"][qid]["claims"]
        
        # Extract Birthdate (Property P569)
        try:
            birth_raw = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
        except (KeyError, IndexError):
            birth_raw = "Not populated on Wikidata"
            
        # Extract Deathdate (Property P570)
        try:
            death_raw = claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"]
        except (KeyError, IndexError):
            death_raw = "Alive / Unknown"
            
        return {
            "name": person_name,
            "qid": qid,
            "birthdate": birth_raw,
            "deathdate": death_raw
            "errormessage": None
        }
        
    except Exception as e:
        return f"Step 2 (Data Claim Fetch) failed: {e}"

# Run verification tests
print(get_person_dates("Albert Einstein"))
print("\n--- Testing with a living person ---")
print(get_person_dates("Keanu Reeves"))