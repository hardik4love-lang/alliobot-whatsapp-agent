import re
import json
import aiohttp
from typing import Optional
from loguru import logger
from app.config import settings
from app.orders.models import ParsedOrder, OrderType, DeliverySlot

SURAT_SUBURBS = [
    "Piplod", "Vesu", "Adajan", "Pal", "Rander", "Varachha", "Katargam",
    "City Light", "Dumas", "Althan", "Bhatar", "Nanpura", "Majura", "Sarthana"
]

def detect_surat_suburb(text: str) -> str:
    for sub in SURAT_SUBURBS:
        if re.search(r'\b' + re.escape(sub) + r'\b', text, re.IGNORECASE):
            return sub
    return "Surat Central"

async def extract_order_from_text(conversation_history_text: str) -> Optional[ParsedOrder]:
    """
    Invokes Ollama with a strict JSON instruction to extract structured order entities.
    Falls back to regex extraction if JSON fails.
    """
    prompt = f"""
Extract order information from this conversation transcript. Output ONLY valid JSON with keys:
- "is_order": boolean (true if customer confirmed an order or asked for sample)
- "restaurant_name": string
- "quantity_kg": number (0.5 if sample requested, otherwise positive number)
- "is_sample": boolean
- "delivery_address": string
- "surat_suburb": string
- "delivery_slot": "MORNING_PREP" or "EVENING_PREP"

Transcript:
\"\"\"{conversation_history_text}\"\"\"
"""
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1}
    }
    ollama_url = f"{settings.OLLAMA_HOST}/api/generate"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ollama_url, json=payload, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    raw_json = json.loads(data.get("response", "{}"))
                    if not raw_json.get("is_order", False):
                        return None

                    is_sample = raw_json.get("is_sample", False)
                    qty = float(raw_json.get("quantity_kg", 0.5 if is_sample else 5.0))
                    address = raw_json.get("delivery_address") or "Surat"
                    suburb = raw_json.get("surat_suburb") or detect_surat_suburb(address)

                    unit_price = settings.DEFAULT_PRICE_PER_KG
                    if qty >= settings.BULK_DISCOUNT_MIN_KG:
                        unit_price = settings.BULK_DISCOUNT_PRICE_PER_KG

                    order = ParsedOrder(
                        restaurant_name=raw_json.get("restaurant_name") or "Surat Commercial Kitchen",
                        quantity_kg=qty,
                        unit_price=unit_price,
                        delivery_address=address,
                        surat_suburb=suburb,
                        delivery_slot=DeliverySlot.MORNING_PREP,
                        payment_mode="COD_UPI",
                        order_type=OrderType.SAMPLE_500G if is_sample else OrderType.COMMERCIAL_ORDER
                    )
                    return order
    except Exception as e:
        logger.error(f"Error in LLM order extraction: {e}")

    # Fallback heuristic: check for 'sample' keyword
    if re.search(r'\b(sample|trial|demo)\b', conversation_history_text, re.IGNORECASE):
        return ParsedOrder(
            restaurant_name="Inquiry Lead",
            quantity_kg=0.5,
            unit_price=0.0,
            delivery_address="Address Pending via Chat",
            surat_suburb=detect_surat_suburb(conversation_history_text),
            order_type=OrderType.SAMPLE_500G
        )

    return None
