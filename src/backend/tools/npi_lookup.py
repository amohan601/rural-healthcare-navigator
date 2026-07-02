# src/backend/tools/npi_lookup.py
# Uses geopy.distance.geodesic for distance calculation
# instead of manual Haversine math.
# geodesic is more accurate — accounts for Earth's ellipsoidal shape.

import requests
from langchain.tools import tool
from geopy.distance import geodesic

NPPES_API = "https://npiregistry.cms.hhs.gov/api/"


# Taxonomy code → readable specialty name
TAXONOMY_MAP = {
    "207R00000X": "Internal Medicine",
    "208000000X": "Pediatrics",
    "207Q00000X": "Family Medicine",
    "207RC0000X": "Cardiology",
    "2084P0800X": "Psychiatry",
    "207X00000X": "Orthopedic Surgery",
    "207RG0100X": "Gastroenterology",
    "207RE0101X": "Endocrinology",
    "207RP1001X": "Pulmonology",
    "207RN0300X": "Nephrology",
    "207V00000X": "Obstetrics & Gynecology",
    "208100000X": "Physical Medicine",
    "261QU0200X": "Urgent Care",
    "261QF0400X": "Federally Qualified Health Center",
    "261QR1300X": "Rural Health Clinic",
    "363L00000X": "Nurse Practitioner",
    "363A00000X": "Physician Assistant",
}


def _get_specialty_name(taxonomies: list) -> str:
    """Convert taxonomy code to readable specialty name."""
    for t in taxonomies:
        code = t.get("code", "")
        if code in TAXONOMY_MAP:
            return TAXONOMY_MAP[code]
        desc = t.get("desc", "")
        if desc:
            return desc
    return "General Practice"


@tool
def npi_lookup_tool(
    specialty: str,
    city: str,
    state: str,
    patient_lat: float,
    patient_lon: float
) -> list:
    """
    Search for healthcare providers by specialty and location
    using the free CMS NPI Registry API.

    Args:
        specialty:   medical specialty e.g. "Cardiology", "Family Medicine"
        city:        city name e.g. "Carrollton"
        state:       two-letter state code e.g. "TX"
        patient_lat: patient latitude for distance calculation
        patient_lon: patient longitude for distance calculation

    Returns:
        List of up to 5 providers sorted by distance, each with
        name, address, phone, specialty, distance_miles, npi number
    """

    TOTAL_RESULTS_EXTRACTED = 5

    params = {
        "version":              "2.1",
        "taxonomy_description": specialty,
        "city":                 city,
        "state":                state,
        "limit":                10,
    }

    try:
        resp = requests.get(NPPES_API, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        return [{"error": str(e)}]

    # Fallback — widen to state only if no city results
    if not results:
        params.pop("city", None)
        try:
            resp    = requests.get(NPPES_API, params=params, timeout=10)
            results = resp.json().get("results", [])
        except Exception:
            return [{"error": f"No providers found for {specialty} in {state}"}]

    patient_coords = (patient_lat, patient_lon)

    providers = []
    for r in results[:TOTAL_RESULTS_EXTRACTED]:
        basic      = r.get("basic", {})
        addresses  = r.get("addresses", [{}])
        taxonomies = r.get("taxonomies", [])
        addr       = addresses[0] if addresses else {}

        # ── Distance via geopy.geodesic ────────────────────────────
        # geodesic is more accurate than Haversine —
        # accounts for Earth's ellipsoidal shape (WGS-84)
        try:
            provider_lat = float(addr.get("latitude")  or 0)
            provider_lon = float(addr.get("longitude") or 0)

            if provider_lat and provider_lon:
                provider_coords = (provider_lat, provider_lon)
                distance_miles  = round(
                    geodesic(patient_coords, provider_coords).miles, 1
                )
            else:
                distance_miles = None


        except Exception:
            distance_miles = None

        # Build name
        name = (
            basic.get("organization_name")
            or f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip()
            or "Unknown Provider"
        )

        providers.append({
            "npi":             r.get("number", ""),
            "name":            name,
            "specialty":       _get_specialty_name(taxonomies),
            "address":         f"{addr.get('address_1', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')}",
            "phone":           addr.get("telephone_number", "N/A"),
            "distance_miles":  distance_miles,
            "fqhc":            False,   # enriched by fqhc_lookup_tool
            "rating":          None,    # enriched by places_detail_tool
            "review_count":    None,    # enriched by places_detail_tool
            "telehealth":      None,    # enriched by places_detail_tool
            "pharmacy_nearby": None,    # enriched by pharmacy_nearby_tool
        })

    # Sort by distance — closest first, None distances go to end
    return sorted(providers, key=lambda x: x["distance_miles"] or 999)