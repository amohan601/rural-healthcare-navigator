# src/backend/tools/geocoding.py

# Uses Nominatim (OpenStreetMap) — free, no API key needed.
# Fix: always append "USA" for zip-only inputs to avoid
# wrong country matches (e.g. 75006 returning Paris, France)
# Include city, state, and state code as well through reverse lookup

import time
from langchain.tools import tool
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

_geocoder = Nominatim(user_agent="rural-healthcare-navigator")

STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

def _try_geocode(query: str):
    """Try one geocode query. Rate limit: 1 req/sec."""
    time.sleep(1)
    return _geocoder.geocode(query, timeout=10)

def _get_city_state(lat: str, lon: str):
    location = _geocoder.reverse(str(lat) +" "+  str(lon))

    # The raw address components
    address = location.raw['address']

    city = city = (
        address.get('city') or
        address.get('town') or
        address.get('village') or
        address.get('hamlet') or
        address.get('suburb') or
        address.get('county')  # last resort
    )
    state = address.get('state')
    state_code = STATE_ABBREV.get(state)
    return city, state,state_code


@tool
def geocode_tool(location: str) -> dict:
    """
    Convert a location string to latitude and longitude coordinates.
    Handles city/state, zip codes, and county names.

    Args:
        location: e.g. "Carrollton TX", "75006", "Austin Texas",
                  "30301", "Phoenix AZ"
    Returns:
        dict with lat, lon, display_name — or error key if failed
    """
    try:
        query = location.strip()

        # Fix: zip-only inputs get USA appended to avoid wrong country
        # e.g. "75006" would return Paris France without this
        if query.replace("-", "").isdigit():
            query = f"{query}, USA"

        # Strategy 1 — try query as-is (with USA fix applied)
        result = _try_geocode(query)

        if result:
            city,state,state_code = _get_city_state(result.latitude,result.longitude)
            return {
                "lat":          result.latitude,
                "lon":          result.longitude,
                "display_name": result.address,
                "city" : city,
                "state" : state,
                "state_code": state_code
            }

        # Strategy 2 — append United States for city/state that didn't match
        result = _try_geocode(f"{location}, United States")
        if result:
            city,state,state_code = _get_city_state(result.latitude,result.longitude)
            return {
                "lat":          result.latitude,
                "lon":          result.longitude,
                "display_name": result.address,
                "city" : city,
                "state" : state,
                "state_code": state_code
            }

        return {
            "error": f"Could not geocode '{location}'. Try 'City, State' format e.g. 'Austin TX'"
        }

    except GeocoderTimedOut:
        return {"error": "Geocoding timed out — try again"}
    except GeocoderServiceError as e:
        return {"error": f"Geocoding service error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}