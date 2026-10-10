import random
import math
from datetime import datetime
import pytz
from app.config import settings
from loguru import logger

IST = pytz.timezone(settings.TIMEZONE)

def is_within_circadian_window() -> bool:
    """
    Checks if current time in Surat (IST) is within allowed commercial outreach hours:
    - Morning Window: 09:30 AM to 11:30 AM IST (Before lunch service)
    - Afternoon Window: 03:30 PM to 05:30 PM IST (Before dinner prep)
    Hard-locks all cold outreach during kitchen rush hours and night hours.
    """
    now = datetime.now(IST)
    hour = now.hour
    minute = now.minute
    total_minutes = hour * 60 + minute

    # 09:30 AM = 570 mins, 11:30 AM = 690 mins
    morning_open = 9 * 60 + 30
    morning_close = 11 * 60 + 30

    # 03:30 PM = 930 mins, 05:30 PM = 1050 mins
    evening_open = 15 * 60 + 30
    evening_close = 17 * 60 + 30

    is_allowed = (morning_open <= total_minutes <= morning_close) or (
        evening_open <= total_minutes <= evening_close
    )
    return is_allowed

def calculate_poisson_jitter_delay() -> float:
    """
    Computes a stochastic dispatch delay using a Poisson Process arrival model.
    Paces single-number outbound messages between 180 and 420 seconds (3 to 7 minutes)
    to completely mimic human one-on-one typing and interaction speeds.
    """
    u = random.random()
    # Avoid log(0)
    u = max(u, 0.0001)

    # Average lambda = 1 message per 270 seconds
    lam = 1.0 / 270.0
    delay = -math.log(u) / lam

    # Clamp between min and max bounds from settings
    clamped_delay = max(
        float(settings.MIN_OUTBOUND_INTERVAL_SECONDS),
        min(float(settings.MAX_OUTBOUND_INTERVAL_SECONDS), delay),
    )
    logger.debug(f"Calculated Poisson jitter delay: {clamped_delay:.1f} seconds")
    return clamped_delay
