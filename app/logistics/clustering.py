from typing import Dict, List, Any
from collections import defaultdict
from loguru import logger

SURAT_ZONES = {
    "ZONE_1_SOUTH": ["Piplod", "Vesu", "Althan", "City Light", "Dumas", "VIP Road"],
    "ZONE_2_WEST": ["Adajan", "Pal", "Rander", "Jahangirpura", "Hazira"],
    "ZONE_3_EAST": ["Varachha", "Katargam", "Sarthana", "Simada", "Hirabaug", "Mota Varachha"],
    "ZONE_4_CORE": ["Nanpura", "Majura", "Rustampura", "Athwa", "Chowk Bazar", "Surat Central", "Ring Road"]
}

ZONE_NAMES = {
    "ZONE_1_SOUTH": "Route 1: South Belt (Vesu, Piplod & City Light)",
    "ZONE_2_WEST": "Route 2: West Belt (Adajan & Pal across Tapi)",
    "ZONE_3_EAST": "Route 3: East Belt (Varachha & Katargam Thali Hub)",
    "ZONE_4_CORE": "Route 4: Core & Ring Road (Nanpura & Athwa)"
}

def resolve_zone(suburb: str) -> str:
    """
    Classifies a Surat suburb into an optimal dispatch zone
    to eliminate cross-river Tapi traffic bottlenecks during 05:00 - 08:00 AM morning prep.
    """
    suburb_lower = (suburb or "").strip().lower()
    for zone, localities in SURAT_ZONES.items():
        if any(loc.lower() in suburb_lower for loc in localities):
            return zone
    return "ZONE_4_CORE"

def generate_morning_dispatch_manifests(orders: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groups confirmed orders into geographically clustered driver manifests.
    """
    manifests = defaultdict(list)
    for ord_item in orders:
        suburb = ord_item.get("surat_suburb") or "Surat Central"
        zone = resolve_zone(suburb)
        manifests[zone].append(ord_item)
    return dict(manifests)

def format_driver_manifest_whatsapp_text(zone: str, order_list: List[Dict[str, Any]], date_str: str) -> str:
    """
    Formats an actionable, driver-friendly WhatsApp task sheet with Google Maps quick links.
    """
    zone_title = ZONE_NAMES.get(zone, zone)
    total_kg = sum(float(o.get("quantity_kg", 0)) for o in order_list)
    total_cod = sum(float(o.get("total_amount", 0)) for o in order_list if o.get("payment_status") != "PAID_UPI")

    lines = [
        f"📋 *DISPATCH MANIFEST - {zone_title.upper()}*",
        f"📅 Date: {date_str} | Slot: 05:00 - 08:00 AM",
        f"📦 Total Load: *{total_kg:.1f} kg* ({len(order_list)} Stops)",
        f"💵 COD Cash to Collect: *₹{total_cod:,.0f}*",
        "─────────────────────────"
    ]

    for idx, ord_item in enumerate(order_list, 1):
        code = ord_item.get("order_code", "ORD")
        rest_name = ord_item.get("restaurant_name", "Kitchen")
        qty = float(ord_item.get("quantity_kg", 0))
        amt = float(ord_item.get("total_amount", 0))
        pay_status = ord_item.get("payment_status", "UNPAID")
        pay_str = "PAID UPI ✅" if pay_status == "PAID_UPI" else f"Collect ₹{amt:,.0f} COD"
        address = ord_item.get("delivery_address", "Surat")
        phone = ord_item.get("phone_e164", "")

        encoded_addr = address.replace(" ", "+")
        map_link = f"https://maps.google.com/?q={encoded_addr}+Surat"

        lines.append(f"{idx}️⃣ *{rest_name}* [{qty:.1f} kg | {pay_str}]")
        lines.append(f"   Ref: `{code}`")
        lines.append(f"   📍 {address}")
        lines.append(f"   🗺️ Map: {map_link}")
        if phone:
            lines.append(f"   📞 Call Chef: {phone}")
        lines.append("")

    lines.append("─────────────────────────")
    lines.append("👉 Driver Action: Reply with `DELIVERED ORD-XXXX` upon completion.")
    return "\n".join(lines)
