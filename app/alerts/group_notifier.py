import aiohttp
from app.config import settings
from app.orders.models import ParsedOrder, OrderType
from loguru import logger

async def dispatch_operations_group_alert(
    order: ParsedOrder,
    customer_phone: str,
    order_code: str
) -> bool:
    """
    Sends a formatted notification to the configured internal operations WhatsApp group
    via Evolution API, alerting the warehouse and dispatch drivers immediately.
    """
    group_jid = settings.OPERATIONS_GROUP_JID
    if not group_jid:
        logger.warning("OPERATIONS_GROUP_JID is not configured. Skipping group alert.")
        return False

    is_sample = order.order_type == OrderType.SAMPLE_500G
    header = "🎁 *NEW TRIAL SAMPLE REQUEST!*" if is_sample else "🚨 *NEW COMMERCIAL ORDER CONFIRMED!*"

    alert_text = f"""{header}
─────────────────────────
📦 *Order Code:* `{order_code}`
🏢 *Kitchen/Restaurant:* {order.restaurant_name}
📞 *Customer Phone:* {customer_phone}
⚖️ *Quantity:* {order.quantity_kg:.1f} kg
💰 *Price/kg:* ₹{order.unit_price:.2f} (Total: ₹{order.total_amount:.2f})
📍 *Delivery Locality:* {order.surat_suburb}
🏠 *Address:* {order.delivery_address}
⏰ *Delivery Slot:* {order.delivery_slot.value}
💳 *Payment Mode:* {order.payment_mode}
─────────────────────────
👉 *Dispatch Action:* Pack in Food-Grade Liner Crate & Assign to Reefer Route ({order.surat_suburb}).
"""

    base_url = settings.EVOLUTION_API_URL
    instance = settings.EVOLUTION_INSTANCE_NAME
    send_url = f"{base_url}/message/sendText/{instance}"

    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "number": group_jid,
        "options": {
            "delay": 500,
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": alert_text
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(send_url, json=payload, headers=headers, timeout=10) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Operations group alert dispatched for {order_code} to {group_jid}")
                    return True
                else:
                    body = await resp.text()
                    logger.error(f"Failed to post to operations group ({resp.status}): {body}")
                    return False
    except Exception as e:
        logger.error(f"Exception posting alert to operations group: {e}")
        return False
