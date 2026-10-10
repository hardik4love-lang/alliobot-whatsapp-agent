import aiohttp
from loguru import logger
from app.config import settings

async def transcribe_voice_note(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """
    Transcribes incoming WhatsApp voice notes (PTT / audio messages) using Groq Whisper-large-v3.
    Includes Gujarati culinary domain prompting to maximize speech recognition accuracy.
    """
    if not settings.GROQ_API_KEY:
        logger.debug("GROQ_API_KEY not configured. Cannot transcribe voice note.")
        return ""

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    # Gujarati culinary domain prompt primes Whisper vocabulary
    initial_prompt = (
        "Surat commercial kitchen B2B garlic sales conversation. "
        "Vocabulary: lahsan, tadka, kilo, bhav, sample, Piplod, Adajan, Vesu, Varachha, "
        "Sardar mandi, Katargam, Kathiyawadi, khata, rokle, delivery slot, 120 per kg."
    )

    data = aiohttp.FormData()
    data.add_field("file", audio_bytes, filename=filename, content_type="audio/ogg")
    data.add_field("model", "whisper-large-v3")
    data.add_field("prompt", initial_prompt)
    data.add_field("response_format", "json")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers, timeout=20) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    transcription = result.get("text", "").strip()
                    logger.info(f"Groq Whisper transcribed voice note: '{transcription}'")
                    return transcription
                else:
                    err = await resp.text()
                    logger.warning(f"Groq Whisper HTTP {resp.status}: {err}")
                    return ""
    except Exception as e:
        logger.warning(f"Voice note transcription error: {e}")
        return ""
