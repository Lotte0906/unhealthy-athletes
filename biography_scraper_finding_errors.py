import requests
from typing import TypedDict
import time
import re

class PersonEntry(TypedDict):
    name: str
    qid: str | None
    number_of_matches: int | None
    matched_search_name: str | None
    birthdate: str | None
    deathdate: str | None
    status: str | None
    mannerofdeath: str | None
    errormessage: str


HEADERS = {
    "User-Agent": (
        "ResearchDataExtractionTool/3.0 "
        "(lottee0906@gmail.com) Python-requests"
    ),
    "Accept": "application/json",
}
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def add_error(person_entry: PersonEntry, message: str) -> None:
    """Append an error message to a person's record and print diagnostics."""
    if person_entry["errormessage"]:
        person_entry["errormessage"] += " | "
    person_entry["errormessage"] += message
    print(f"[{person_entry['name']} | QID: {person_entry['qid']}] {message}")

def clean_person_name(person_name):
    """Remove a trailing parenthetical part from a person's name."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", person_name).strip()

def attempt_find_wikidata_entry(person_name, headers=HEADERS):
    person_entry = {
        "name": person_name,
        "qid": None,
        "number_of_matches": None,
        "matched_search_name": None,
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": ""
    }

    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": person_name,
        "language": "en",
        "format": "json",
        "formatversion": 2,
        "limit": 50
    }

    max_attempts = 3
    wait_times = [5, 10]

    for attempt in range(max_attempts):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            search_response = response.json()

        except (requests.RequestException, ValueError) as error:
            add_error(
                person_entry,
                f"Technical error during Wikidata search: {error}"
            )
            return person_entry

        search_results = search_response.get("search")

        if not isinstance(search_results, list):
            error = search_response.get("error", {})
            error_code = error.get("code")

            if error_code == "cirrussearch-too-busy-error":
                if attempt < max_attempts - 1:
                    wait_time = wait_times[attempt]
                    print(
                        f"[{person_name}] Wikidata search is busy. "
                        f"Retrying in {wait_time} seconds "
                        f"(attempt {attempt + 2}/{max_attempts})."
                    )
                    time.sleep(wait_time)
                    continue

                add_error(
                    person_entry,
                    "Wikidata search remained too busy after "
                    f"{max_attempts} attempts"
                )
                return person_entry

            add_error(
                person_entry,
                f"Wikidata returned unexpected response: {search_response}"
            )
            return person_entry

        # A valid search response was received.
        person_entry["number_of_matches"] = len(search_results)

        if search_results:
            person_entry["qid"] = search_results[0]["id"]
            person_entry["matched_search_name"] = person_name

        return person_entry

    return person_entry

def find_wikidata_entry(
    person_name: str, headers: dict = HEADERS
) -> PersonEntry:
    """Try name variations and return the first variation that finds a QID."""
    person_entry: PersonEntry = {
        "name": person_name,
        "qid": None,
        "number_of_matches": 0,
        "matched_search_name": None,
        "birthdate": None,
        "deathdate": None,
        "status": None,
        "mannerofdeath": None,
        "errormessage": "",
    }
    
    search_name = clean_person_name(person_name)
    name_parts = search_name.split()
    if not name_parts:
        add_error(person_entry, "Empty athlete name")
        return person_entry

    name_variations = [
        search_name,
        f"{name_parts[0]} {name_parts[-1]}",
    ]
    if len(name_parts) >= 3:
        name_variations.append(f"{name_parts[0]} {' '.join(name_parts[-2:])}")

    # Remove duplicate variations while preserving their order.
    name_variations = list(dict.fromkeys(name_variations))
    technical_errors = []

    for search_name in name_variations:
        entry = attempt_find_wikidata_entry(search_name, headers=headers)
        if entry["qid"] is not None:
            entry["name"] = person_name
            return entry
        if entry["errormessage"]:
            technical_errors.append(entry["errormessage"])

    if technical_errors:
        for message in technical_errors:
            add_error(person_entry, message)
    else:
        add_error(
            person_entry,
            "No Wikidata search results found for any name variation",
        )
    return person_entry


def get_entity_data(qid, headers=HEADERS):
    """Fetch Wikidata entity data, retrying temporary connection errors."""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "claims|sitelinks",
        "format": "json",
        "formatversion": 2
    }

    wait_times = [5, 10]
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            raw_data = response.json()

            # Check that the response contains the expected entity.
            entities = raw_data.get("entities")
            if not isinstance(entities, dict) or qid not in entities:
                raise ValueError(
                    f"Wikidata response did not contain entity {qid}"
                )

            raw_data["qid"] = qid
            return raw_data

        except (requests.ConnectionError, requests.Timeout) as error:
            if attempt < max_attempts - 1:
                wait_time = wait_times[attempt]
                print(
                    f"[QID: {qid}] Connection error: {error}. "
                    f"Retrying in {wait_time} seconds "
                    f"(attempt {attempt + 2}/{max_attempts})."
                )
                time.sleep(wait_time)
            else:
                print(
                    f"[QID: {qid}] Fetching Wikidata entity failed "
                    f"after {max_attempts} attempts: {error}"
                )
                raise

    return None


def check_date(date: str, datetype: str) -> tuple[str, str]:
    """Replace unknown month/day values ('00') with '01' and describe them."""
    if not isinstance(date, str) or len(date) < 11:
        raise ValueError(f"Unexpected Wikidata {datetype} format: {date!r}")

    missing = []
    if date[6:8] == "00":
        date = date[:6] + "01" + date[8:]
        missing.append("month")
    if date[9:11] == "00":
        date = date[:9] + "01" + date[11:]

    if len(missing) == 1:
        message = f"{missing[0]} of {datetype} is missing"
    elif len(missing) == 2:
        message = f"{missing[0]} and {missing[1]} of {datetype} are missing"
    else:
        message = ""
    return date, message


def check_if_alive_on_wikipedia(
    entity_data: dict, headers: dict = HEADERS
) -> str | None:
    """Return 'Alive' if the linked English Wikipedia page is in Living people."""
    qid = entity_data.get("qid")
    if not qid:
        raise ValueError("Entity data is missing the QID")

    entity = entity_data.get("entities", {}).get(qid, {})
    enwiki = entity.get("sitelinks", {}).get("enwiki")
    if not isinstance(enwiki, dict) or not enwiki.get("title"):
        return None

    wp_params = {
        "action": "query",
        "titles": enwiki["title"],
        "prop": "categories",
        "clcategories": "Category:Living people",
        "format": "json",
    }
    response = requests.get(
        WIKIPEDIA_API_URL, params=wp_params, headers=headers, timeout=10
    )
    response.raise_for_status()
    wp_data = response.json()

    pages = wp_data.get("query", {}).get("pages", {})
    if not isinstance(pages, dict) or not pages:
        raise ValueError("Wikipedia response did not contain any page data")
    page = next(iter(pages.values()))
    return "Alive" if "categories" in page else None


def get_label_from_qid(qid: str, headers: dict = HEADERS) -> str:
    """Fetch the English label for a Wikidata QID."""
    if not isinstance(qid, str) or not qid.startswith("Q"):
        raise ValueError(f"Invalid Wikidata QID: {qid!r}")

    params = {
        "action": "wbgetentities", "ids": qid, "languages": "en",
        "props": "labels", "format": "json", "formatversion": "2",
    }
    response = requests.get(
        WIKIDATA_API_URL, params=params, headers=headers, timeout=10
    )
    response.raise_for_status()
    label_data = response.json()
    try:
        return label_data["entities"][qid]["labels"]["en"]["value"]
    except (KeyError, TypeError) as e:
        raise ValueError(f"No English label found for {qid}") from e


def get_wikidata_claims(
    person_entry: PersonEntry, headers: dict = HEADERS
) -> PersonEntry:
    """Extract birth/death dates and death details for one person."""
    qid = person_entry["qid"]
    if not qid:
        if not person_entry["errormessage"]:
            add_error(person_entry, "No QID available; cannot retrieve claims")
        return person_entry

    try:
        raw_data = get_entity_data(qid, headers=headers)
    except requests.RequestException as e:
        add_error(person_entry, f"Fetching Wikidata entity failed: {e}")
        return person_entry
    except (ValueError, KeyError, TypeError) as e:
        add_error(person_entry, f"Unexpected Wikidata entity response: {e}")
        return person_entry

    claims = raw_data["entities"][qid].get("claims", {})
    if not isinstance(claims, dict):
        add_error(person_entry, "Wikidata claims field had an unexpected format")
        return person_entry

    # Birth date (P569). A missing birth date is missing data, not an error.
    try:
        raw_date = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
        person_entry["birthdate"], message = check_date(raw_date, "birth")
        if message:
            add_error(person_entry, message)
    except (KeyError, IndexError, TypeError):
        person_entry["birthdate"] = None
    except ValueError as e:
        add_error(person_entry, f"Could not interpret birth date: {e}")
        person_entry["birthdate"] = None

    # Death date (P570). If absent, consult the linked Wikipedia page.
    try:
        raw_date = claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"]
        person_entry["deathdate"], message = check_date(raw_date, "death")
        person_entry["status"] = "Dead"
        if message:
            add_error(person_entry, message)
    except (KeyError, IndexError, TypeError):
        person_entry["deathdate"] = None
        entity_data = dict(raw_data)
        entity_data["qid"] = qid
        try:
            person_entry["status"] = check_if_alive_on_wikipedia(
                entity_data, headers=headers
            )
        except requests.RequestException as e:
            add_error(person_entry, f"Wikipedia living-status request failed: {e}")
        except (ValueError, KeyError, TypeError) as e:
            add_error(person_entry, f"Could not check Wikipedia living status: {e}")
    except ValueError as e:
        add_error(person_entry, f"Could not interpret death date: {e}")
        person_entry["deathdate"] = None

    # Manner of death (P1196), falling back to cause of death (P509).
    if person_entry["status"] == "Dead":
        manner_qid = None
        for property_id in ("P1196", "P509"):
            try:
                manner_qid = claims[property_id][0]["mainsnak"]["datavalue"]["value"]["id"]
                if manner_qid:
                    break
            except (KeyError, IndexError, TypeError):
                continue

        if manner_qid:
            try:
                person_entry["mannerofdeath"] = get_label_from_qid(
                    manner_qid, headers=headers
                )
            except requests.RequestException as e:
                add_error(person_entry, f"Could not fetch manner-of-death label: {e}")
            except (ValueError, KeyError, TypeError) as e:
                add_error(person_entry, f"Could not interpret manner of death: {e}")

    return person_entry
