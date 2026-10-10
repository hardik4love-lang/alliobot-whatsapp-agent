import re
from typing import Tuple, Optional

OPT_OUT_KEYWORDS = ["stop", "unsubscribe", "nathi joytu", "nahi chahiye", "block", "dont message", "no"]

PRICE_OBJECTION_KEYWORDS = ["120 rate", "local vendor", "sasta", "cheaper", "bhav vadhare", "rate high", "100 ma", "105"]

QUALITY_OBJECTION_KEYWORDS = ["pani", "water", "kharab", "spoil", "green", "slime", "tadka", "pan test"]

def check_opt_out(user_text: str) -> bool:
    """
    Checks if lead has requested immediate opt-out / unsubscription.
    """
    text = user_text.lower().strip()
    return any(kw in text for kw in OPT_OUT_KEYWORDS)

def detect_objection_context(user_text: str) -> Optional[str]:
    """
    Categorizes the primary objection from customer text.
    """
    text = user_text.lower()
    if any(kw in text for kw in PRICE_OBJECTION_KEYWORDS):
        return "PRICE_OBJECTION"
    if any(kw in text for kw in QUALITY_OBJECTION_KEYWORDS):
        return "QUALITY_OBJECTION"
    return None
