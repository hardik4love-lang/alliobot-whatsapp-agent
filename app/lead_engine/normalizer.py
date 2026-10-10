import phonenumbers
from typing import Optional
from loguru import logger

def normalize_phone_number(raw_phone: str, default_region: str = "IN") -> Optional[str]:
    """
    Normalizes raw telephone numbers to strict E.164 (+91XXXXXXXXXX) format.
    Explicitly filters out landlines, invalid lengths, and non-mobile carrier codes.
    """
    if not raw_phone:
        return None
    try:
        cleaned = "".join(ch for ch in raw_phone if ch.isdigit() or ch == "+")
        parsed = phonenumbers.parse(cleaned, default_region)

        if not phonenumbers.is_valid_number(parsed):
            return None

        # Rejection of Surat STD landline (0261)
        num_type = phonenumbers.number_type(parsed)
        if num_type not in (
            phonenumbers.PhoneNumberType.MOBILE,
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
        ):
            logger.debug(f"Rejecting non-mobile phone number: {raw_phone} (Type: {num_type})")
            return None

        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return formatted
    except Exception as e:
        logger.debug(f"Failed to parse phone number '{raw_phone}': {e}")
        return None
