import requests
from requests.exceptions import HTTPError, RequestException, JSONDecodeError
from datetime import datetime



def make_user(first: str, last: str, year: int) -> dict:
    return {
        "name": {"first": first, "last": last, "title": "Mr"},
        "dob": {"date": f"{year}-06-15T00:00:00.000Z"}  # ← match real API shape
    }
 
def get_users(results: int = 20) -> list:
    """Fetches random user data from randomuser.me API."""
    if results < 1 or results > 5000:
        raise ValueError("results must be between 1 and 5000")
 
    url = f"https://randomuser.me/api/?results={results}"
 
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
 
        data = response.json()
        return data["results"]
 
    except HTTPError as e:
        status = getattr(response, "status_code", "unknown")  # fix: response may be unbound
        print(f"HTTP error {status}: {e}")
        raise
    except JSONDecodeError:
        print("Failed to parse JSON response")
        raise
    except KeyError:
        print("Unexpected API response structure (missing 'results' key)")
        raise
    except RequestException as e:
        print(f"Request failed: {e}")
        raise
 


def _birth_year(user: dict) -> int:
    dob_str = user["dob"]["date"]
    return datetime.fromisoformat(dob_str.replace("Z", "+00:00")).year


def filter_users_born_on_or_before(users: list, year: int = 2000) -> list:
    """Return user records born in or before the given year (Exercise 2 filter)."""
    return [u for u in users if _birth_year(u) <= year]


def format_users(users: list) -> list[str]:
    """
    Returns a list of 'FirstName LastName' strings
    for users born on or before 31 Dec 2000.
    """
    result = []
    for user in filter_users_born_on_or_before(users):
        first = user["name"]["first"]
        last = user["name"]["last"]
        result.append(f"{first} {last}")
    return result


