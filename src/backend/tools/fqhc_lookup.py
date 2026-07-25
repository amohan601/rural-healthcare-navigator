# src/backend/tools/fqhc_lookup.py
# DAY 3 — UPDATED (Option A)
#
# Checks if a SPECIFIC provider from npi_lookup_tool is an FQHC.
# Downloads HRSA FQHC site CSV once, queries locally.
# No API token needed.
#
# CHANGE: _load_fqhc_sites() returns tuple (not list)
# WHY: lru_cache requires hashable return type — list is not hashable

import os
import csv
import requests
from langchain.tools import tool
from functools import lru_cache
from src.backend.logging.logger import logger

HRSA_CSV_URL = "https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv"
LOCAL_CSV    = "src/backend/data/fqhc_sites.csv"


def _download_fqhc_csv():
    """Download HRSA FQHC CSV once and cache locally."""
    os.makedirs("src/backend/data", exist_ok=True)
    if os.path.exists(LOCAL_CSV):
        logger.info("[fqhc] Using cached FQHC CSV")
        return True
    try:
        logger.info("[fqhc] Downloading HRSA FQHC site list...")
        resp = requests.get(HRSA_CSV_URL, timeout=30)
        resp.raise_for_status()
        with open(LOCAL_CSV, "wb") as f:
            f.write(resp.content)
        logger.info(f"[fqhc] Saved → {LOCAL_CSV}")
        return True
    except Exception as e:
        logger.error(f"[fqhc] Download failed: {e}")
        return False


@lru_cache(maxsize=1)
def _load_fqhc_sites() -> tuple:
    """
    Load FQHC sites from local CSV into memory.
    Returns tuple — lru_cache requires hashable return type.
    Convert back to list at call site with list(_load_fqhc_sites()).
    """
    sites = []
    try:
        with open(LOCAL_CSV, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sites.append(row)
        logger.info(f"[fqhc] Loaded {len(sites)} FQHC sites")
    except Exception as e:
        logger.error(f"[fqhc] Error loading CSV: {e}")
    return tuple(sites)


@tool
def fqhc_lookup_tool(provider_name: str, state: str) -> dict:
    """
    Check if a specific healthcare provider is a Federally Qualified
    Health Center (FQHC). Call this for each provider returned by
    npi_lookup_tool to check sliding scale eligibility.

    FQHCs are legally required to see patients regardless of ability
    to pay. Patients pay on a sliding scale based on income.

    Args:
        provider_name: provider name from npi_lookup_tool
                       e.g. "Metrocare Services"
        state:         two-letter state code e.g. "TX"

    Returns:
        dict with is_fqhc (bool), sliding_scale (bool),
        matched_name, note
    """
    # Download CSV if not cached
    if not os.path.exists(LOCAL_CSV):
        success = _download_fqhc_csv()
        if not success:
            return {
                "is_fqhc":       False,
                "sliding_scale": False,
                "note":          "Could not load FQHC data — check internet connection"
            }

    # Convert tuple back to list for iteration
    sites          = list(_load_fqhc_sites())
    provider_lower = provider_name.lower().strip()

    # Filter by state first for faster matching
    state_sites = [
        s for s in sites
        if (s.get("Site State Abbreviation") or "").upper() == state.upper()
    ]

    # Match on meaningful words in provider name (skip short words)
    search_words = [w for w in provider_lower.split() if len(w) > 3]

    for site in state_sites:
        site_name = (site.get("Site Name") or "").lower()

        if any(word in site_name for word in search_words):
            return {
                "is_fqhc":       True,
                "sliding_scale": True,
                "matched_name":  site.get("Site Name"),
                "address":       f"{site.get('Site Address', '')} {site.get('Site City', '')} {site.get('Site State Abbreviation', '')} {site.get('Site Postal Code', '')}".strip(),
                "phone":         site.get("Site Telephone Number", "N/A"),
                "note":          "FQHC — sliding scale fees based on income. No one turned away."
            }

    return {
        "is_fqhc":       False,
        "sliding_scale": False,
        "matched_name":  None,
        "note":          "Not an FQHC — standard billing applies"
    }