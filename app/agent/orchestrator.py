import aiohttp
import json
from typing import List, Dict, Any
from loguru import logger
from app.config import settings
from app.agent.prompts import SYSTEM_SALES_PROMPT
from app.agent.objection_engine import check_opt_out
from app.agent.cloud_ai_pool import cloud_ai_pool

async def generate_sales_response(
    messages_history: List[Dict[str, str]],
    user_latest_message: str
) -> str:
    """
    Sends conversation history + latest message to the Free Cloud AI Pool (Groq / GitHub Models / OpenRouter).
    Falls back to local Ollama or deterministic script only if all cloud providers fail.
    """
    if check_opt_out(user_latest_message):
        return "Samji gaya bhai. Tamare number par thi aagad message nahi aave. Aabhar."

    formatted_messages = [{"role": "system", "content": SYSTEM_SALES_PROMPT}]
    for msg in messages_history[-6:]:  # Keep recent 6 turns for context
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    formatted_messages.append({"role": "user", "content": user_latest_message})

    # Step 1: Query Free Cloud AI Pool (Zero local download, blazing fast)
    cloud_reply = await cloud_ai_pool.chat_completion(
        messages=formatted_messages,
        temperature=0.35,
        max_tokens=180
    )
    if cloud_reply:
        return cloud_reply

    # Step 2: Fallback to local Ollama if configured
    logger.info("Attempting local Ollama fallback...")
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
            async with session.post(ollama_url, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    bot_text = data.get("message", {}).get("content", "").strip()
                    return bot_text
    except Exception as e:
        logger.debug(f"Local Ollama unreachable or skipped: {e}")

    # Step 3: Deterministic high-converting script fallback (Fresh peeled garlic, paid trial pack)
    return "Namaste! VedicAllio taaju folelu lasan (100% fresh raw peeled garlic) ₹120/kg ma available che. Kal savaare kitchen test mate 1-2 kg trial pack mocklavu? Tamari restaurant nu address share karsho."

