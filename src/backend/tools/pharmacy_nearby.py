# src/backend/tools/pharmacy_nearby.py
# DAY 3 — UPDATED
#
# Uses Google Places API (New) via direct HTTP requests.
# Replaces googlemaps library which uses legacy API.
# Uses same GOOGLE_PLACES_API_KEY from .env

import os
import requests
from langchain.tools import tool
from geopy.distance import geodesic

PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"


@tool
def pharmacy_nearby_tool(lat: float, lon: float) -> dict:
    """
    Find the nearest pharmacy to a given location.
    Call this after identifying the top provider so the patient
    knows where to fill prescriptions after their visit.

    Args:
        lat: latitude of provider or patient location
        lon: longitude of provider or patient location

    Returns:
        dict with name, address, distance_miles, open_now
        or error key if none found
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_PLACES_API_KEY not set in .env"}

    headers = {
        "Content-Type":     "application/json",
        "X-Goog-Api-Key":   api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.currentOpeningHours"
    }

    body = {
        "includedTypes": ["drugstore", "pharmacy"],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lon},
                "radius": 8000.0      # 8km ~ 5 miles
            }
        }
    }

    try:
        resp = requests.post(PLACES_URL, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        places = resp.json().get("places", [])

        if not places:
            return {"error": "No pharmacy found within 5 miles"}

        top      = places[0]
        loc      = top.get("location", {})
        pharmacy = (loc.get("latitude"), loc.get("longitude"))
        distance = round(geodesic((lat, lon), pharmacy).miles, 1)

        hours    = top.get("currentOpeningHours", {})

        return {
            "name":           top.get("displayName", {}).get("text", "Unknown Pharmacy"),
            "address":        top.get("formattedAddress", "N/A"),
            "distance_miles": distance,
            "open_now":       hours.get("openNow")
        }

    except requests.exceptions.HTTPError as e:
        return {"error": f"Places API error: {resp.text}"}
    except Exception as e:
        return {"error": f"Pharmacy search failed: {str(e)}"}