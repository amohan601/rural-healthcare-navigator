# src/backend/tools/places_detail.py
# DAY 3 — UPDATED
#
# Uses Google Places API (New) via direct HTTP requests.
# All field names match the New Places API — not the legacy API.

import os
import requests
from langchain.tools import tool


PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"


@tool
def places_detail_tool(provider_name: str, address: str) -> dict:
    """
    Look up a healthcare provider on Google Places (New API) to get
    rating, review count, opening hours, weekday hours, and telehealth flag.

    Args:
        provider_name: name e.g. "Metrocare Services"
        address:       full address string for accurate matching

    Returns:
        dict with rating, review_count, open_now,
        weekday_hours, telehealth
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_PLACES_API_KEY not set in .env"}

    headers = {
        "Content-Type":   "application/json",
        "X-Goog-Api-Key": api_key,
        # Field mask tells API exactly what to return
        "X-Goog-FieldMask": (
            "places.displayName,"
            "places.rating,"
            "places.userRatingCount,"
            "places.currentOpeningHours.openNow,"
            "places.currentOpeningHours.weekdayDescriptions,"
            "places.reviews.text"
        )
    }

    body = {
        "textQuery": f"{provider_name} {address}"
    }

    try:
        resp = requests.post(
            PLACES_SEARCH_URL,
            json=body,
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        places = resp.json().get("places", [])

        if not places:
            return {"error": f"No Places result found for {provider_name}"}

        place = places[0]

        # ── Opening hours ──────────────────────────────────────────
        hours           = place.get("currentOpeningHours", {})
        open_now        = hours.get("openNow")
        weekday_hours   = hours.get("weekdayDescriptions", [])
        # e.g. ["Monday: 8:00 AM – 5:00 PM", "Tuesday: 8:00 AM – 5:00 PM", ...]

        # ── Telehealth detection from reviews ──────────────────────
        reviews = place.get("reviews", [])
        review_text = " ".join(
            r.get("text", {}).get("text", "")
            for r in reviews
        ).lower()
        telehealth = any(
            word in review_text
            for word in ["telehealth", "telemedicine", "virtual visit", "video visit"]
        )

        return {
            "rating":        place.get("rating"),           # e.g. 4.2
            "review_count":  place.get("userRatingCount"),  # e.g. 127
            "open_now":      open_now,                      # True/False/None
            "weekday_hours": weekday_hours,                  # list of strings
            "telehealth":    telehealth                      # True/False
        }

    except requests.exceptions.HTTPError:
        return {"error": f"Places API error: {resp.text}"}
    except Exception as e:
        return {"error": f"Places lookup failed: {str(e)}"}