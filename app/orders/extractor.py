import re
import json
import aiohttp
from typing import Optional
from loguru import logger
from app.config import settings
from app.orders.models import ParsedOrder, OrderType, DeliverySlot

from app.agent.cloud_ai_pool import cloud_ai_pool

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
    Invokes Free Cloud AI Pool with strict JSON instruction to extract structured order entities.
    Falls back to local Ollama or regex heuristics if cloud fails.
    """
    extraction_prompt = f"""
You are an entity extractor. Extract order information from this conversation transcript. Output ONLY valid JSON with keys:
- "is_order": boolean (true if customer confirmed an order or asked for a sample)
- "restaurant_name": string
- "quantity_kg": number (0.5 if sample requested, otherwise positive number)
- "is_sample": boolean
- "delivery_address": string
- "surat_suburb": string
- "delivery_slot": "MORNING_PREP" or "EVENING_PREP"

Transcript:
\"\"\"{conversation_history_text}\"\"\"
"""
    messages = [
        {"role": "system", "content": "You are a JSON-only entity extractor. Respond strictly with JSON."},
        {"role": "user", "content": extraction_prompt}
    ]

    # Try Cloud AI Pool first
    cloud_json_str = await cloud_ai_pool.chat_completion(
        messages=messages,
        temperature=0.1,
        max_tokens=300,
        response_format={"type": "json_object"}
    )

    raw_json = None
    if cloud_json_str:
        try:
            # Handle potential markdown fence wrap
            clean_str = cloud_json_str.strip()
            if clean_str.startswith("```"):
                clean_str = clean_str.split("```")[1]
                if clean_str.startswith("json"):
                    clean_str = clean_str[4:]
            raw_json = json.loads(clean_str.strip())
        except Exception as e:
            logger.debug(f"Cloud AI JSON parsing error: {e}")

    # Fallback to Ollama if cloud did not yield valid JSON
    if not raw_json:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": extraction_prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1}
        }
        ollama_url = f"{settings.OLLAMA_HOST}/api/generate"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(ollama_url, json=payload, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_json = json.loads(data.get("response", "{}"))
        except Exception:
            pass

    try:
        if raw_json and raw_json.get("is_order", False):
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

    # Fallback heuristic: check for 'sample' or 'trial' keyword
    if re.search(r'\b(sample|trial|demo)\b', conversation_history_text, re.IGNORECASE):
        return ParsedOrder(
            restaurant_name="Inquiry Lead",
            quantity_kg=1.0,
            unit_price=settings.DEFAULT_PRICE_PER_KG,
            delivery_address="Address Pending via Chat",
            surat_suburb=detect_surat_suburb(conversation_history_text),
            order_type=OrderType.SAMPLE_500G
        )

    return None
