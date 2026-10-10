import asyncio
import aiohttp
from app.config import settings
from loguru import logger

async def simulate_human_presence_and_send(
    phone_e164: str,
    message_text: str
) -> bool:
    """
    Interacts with Evolution API to mimic human presence before message dispatch:
    1. Sends 'composing' (typing...) state for duration proportional to message length
    2. Sends the text payload
    3. Clears presence state
    """
    clean_number = phone_e164.replace("+", "").strip()
    base_url = settings.EVOLUTION_API_URL
    instance = settings.EVOLUTION_INSTANCE_NAME
    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    # Typing duration: between 2.0 and 6.0 seconds based on character count
    typing_seconds = min(6.0, max(2.0, len(message_text) * 0.05))

    async with aiohttp.ClientSession() as session:
        # Step 1: Send 'composing' status
        presence_url = f"{base_url}/chat/sendPresence/{instance}"
        presence_payload = {
            "number": clean_number,
            "presence": "composing",
            "delay": int(typing_seconds * 1000)
        }
        try:
            await session.post(presence_url, json=presence_payload, headers=headers, timeout=5)
        except Exception as e:
            logger.debug(f"Presence emission skipped or timed out: {e}")

        # Wait for simulated typing
        await asyncio.sleep(typing_seconds)

        # Step 2: Send Message payload
        send_url = f"{base_url}/message/sendText/{instance}"
        payload = {
            "number": clean_number,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": message_text
            }
        }
        try:
            async with session.post(send_url, json=payload, headers=headers, timeout=10) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Message successfully dispatched to {phone_e164}")
                    return True
                else:
                    body = await resp.text()
                    logger.error(f"Evolution API dispatch error ({resp.status}): {body}")
                    return False
        except Exception as e:
            logger.error(f"Failed to dispatch message to {phone_e164}: {e}")
            return False
