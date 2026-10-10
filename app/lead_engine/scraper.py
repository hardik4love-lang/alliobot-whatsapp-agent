import requests
from typing import List, Dict, Any
from loguru import logger
from app.lead_engine.normalizer import normalize_phone_number

# OpenStreetMap Overpass API endpoint (FOSS, Zero Cost)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bounding box for Surat Metropolitan Area (South, West, North, East)
SURAT_BBOX = "21.05,72.70,21.30,72.95"

def scrape_surat_food_amenities() -> List[Dict[str, Any]]:
    """
    Queries OpenStreetMap Overpass QL for restaurants, dhabas, caterers,
    and fast-food establishments within the Surat metropolitan region.
    Extracts commercial names, geographic coordinates, and normalized phones.
    """
    query = f"""
    [out:json][timeout:90];
    (
      node["amenity"~"restaurant|fast_food|cafe"]({SURAT_BBOX});
      way["amenity"~"restaurant|fast_food|cafe"]({SURAT_BBOX});
    );
    out center tags;
    """
    logger.info("Executing Overpass QL extraction for Surat foodservice amenities...")
    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=120)
        response.raise_for_status()
        data = response.json()
        elements = data.get("elements", [])
        logger.info(f"Retrieved {len(elements)} raw spatial elements from OpenStreetMap.")

        valid_leads = []
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            raw_phone = tags.get("contact:phone") or tags.get("phone") or tags.get("contact:mobile")

            if not name or not raw_phone:
                continue

            normalized_phone = normalize_phone_number(raw_phone)
            if not normalized_phone:
                continue

            suburb = tags.get("addr:suburb") or tags.get("addr:neighbourhood") or "Surat"
            street = tags.get("addr:street") or ""
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")

            valid_leads.append({
                "business_name": name,
                "phone_e164": normalized_phone,
                "cuisine_type": tags.get("cuisine", "general"),
                "surat_suburb": suburb,
                "full_address": f"{street}, {suburb}, Surat".strip(", "),
                "source": "OpenStreetMap_Surat",
                "latitude": lat,
                "longitude": lon,
            })

        logger.info(f"Extracted and normalized {len(valid_leads)} valid mobile leads with Surat tags.")
        return valid_leads
    except Exception as e:
        logger.error(f"Error executing Overpass extraction: {e}")
        return []
