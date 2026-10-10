import aiohttp
import json
from typing import List, Dict, Any
from loguru import logger
from app.config import settings
from app.agent.prompts import SYSTEM_SALES_PROMPT
from app.agent.objection_engine import check_opt_out

async def generate_sales_response(
    messages_history: List[Dict[str, str]],
    user_latest_message: str
) -> str:
    """
    Sends conversation history + latest message to self-hosted Ollama (Qwen-2.5-7B)
    and returns conversational reply.
    """
    if check_opt_out(user_latest_message):
        return "Samji gaya bhai. Tamare number par thi aagad message nahi aave. Aabhar."

    formatted_messages = [{"role": "system", "content": SYSTEM_SALES_PROMPT}]
    for msg in messages_history[-6:]:  # Keep recent 6 turns for context
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    formatted_messages.append({"role": "user", "content": user_latest_message})

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": formatted_messages,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
            "num_predict": 180
        }
    }

    ollama_url = f"{settings.OLLAMA_HOST}/api/chat"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ollama_url, json=payload, timeout=25) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    bot_text = data.get("message", {}).get("content", "").strip()
                    return bot_text
                else:
                    err_text = await resp.text()
                    logger.error(f"Ollama API error ({resp.status}): {err_text}")
                    return "Bhai, ame 100% dry peeled lahsan ₹120/kg ma deliver kariye chhiye. Tamare kale morning mate ek 500g trial sample joyiye che?"
    except Exception as e:
        logger.error(f"Failed to reach Ollama inference engine: {e}")
        # Deterministic offline fallback
        return "Namaste! VedicAllio peeled garlic ₹120/kg ma available che. Kale morning prep mate 500g free sample mocklavu? Tamari restaurant nu address share karsho."
