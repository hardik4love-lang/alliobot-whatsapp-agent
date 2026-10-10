import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import settings

class CloudAIPool:
    """
    Resilient Multi-Provider Free Cloud AI Pool with automatic failover.
    Routes queries across zero-cost cloud APIs:
    1. GitHub Models (Free with any GitHub personal token)
    2. Groq Cloud (Free high-speed Llama 3.3 70B)
    3. OpenRouter Free Pool (Free Llama 3.3 / Qwen 2.5 72B)
    4. Google Gemini API (Free Flash tier)
    """

    def __init__(self):
        self.providers = []
        self._initialize_providers()

    def _initialize_providers(self):
        # 1. GitHub Models (Default Free Cloud Tier)
        github_token = settings.GITHUB_TOKEN
        if github_token:
            self.providers.append({
                "name": "GitHub Models (Azure AI)",
                "url": "https://models.inference.ai.azure.com/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {github_token}",
                    "Content-Type": "application/json"
                },
                "model": "meta-llama-3.1-70b-instruct",
            })

        # 2. Groq Cloud (Ultra-Fast Free Tier)
        groq_key = settings.GROQ_API_KEY
        if groq_key:
            self.providers.append({
                "name": "Groq Cloud Free",
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                },
                "model": "llama-3.3-70b-versatile",
            })

        # 3. OpenRouter Free Pool
        openrouter_key = settings.OPENROUTER_API_KEY
        if openrouter_key:
            self.providers.append({
                "name": "OpenRouter Free Pool",
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/hardik4love-lang/alliobot-whatsapp-agent",
                    "X-Title": "AllioBot Surat Garlic Sales"
                },
                "model": "meta-llama/llama-3.3-70b-instruct:free",
            })

        # 4. Google Gemini OpenAI-compatible Free Tier
        gemini_key = settings.GEMINI_API_KEY
        if gemini_key:
            self.providers.append({
                "name": "Google Gemini Free",
                "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {gemini_key}",
                    "Content-Type": "application/json"
                },
                "model": "gemini-1.5-flash",
            })

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 250,
        response_format: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Executes a completion request across the cloud AI pool with automatic failover.
        """
        if not self.providers:
            logger.warning("No Cloud AI API keys configured in pool. Falling back to local/default.")
            return None

        for provider in self.providers:
            p_name = provider["name"]
            url = provider["url"]
            headers = provider["headers"]
            model = provider["model"]

            payload: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                payload["response_format"] = response_format

            try:
                logger.info(f"Querying Cloud AI Pool -> [{p_name}] using model '{model}'...")
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers, timeout=20) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            choices = data.get("choices", [])
                            if choices:
                                content = choices[0].get("message", {}).get("content", "").strip()
                                logger.info(f"Successfully received response from [{p_name}].")
                                return content
                        else:
                            body = await resp.text()
                            logger.warning(f"Provider [{p_name}] returned HTTP {resp.status}: {body}. Failing over to next provider...")
            except Exception as e:
                logger.warning(f"Exception connecting to [{p_name}]: {e}. Failing over...")

        logger.error("All Cloud AI Pool providers exhausted or failed.")
        return None

cloud_ai_pool = CloudAIPool()
