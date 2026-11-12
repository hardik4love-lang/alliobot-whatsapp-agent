import random
import re

SPINTAX_OUTBOUND_TEMPLATES = [
    (
        "{Namaste|Kem cho|Pranam} {Bhai|Chef|Owner Ji}, "
        "{VedicAllio Surat taraf thi Kishan bolu chhu|Surat garlic supply taraf thi navi service sharu thay che}. "
        "21st thi amari navi doorstep delivery scheme sharu thay che — {tamara restaurant na|tamara kitchen na} doorstep par "
        "clean, sorted natural whole garlic bulbs (10kg/20kg કટ્ટા) direct deliver thase. "
        "Distance mujab fakt ₹20 thi ₹50 delivery charge che, APMC javani jarur nathi. "
        "{21st mate tamaro slot pre-book karvo che?|Navi scheme ma tamari kitchen mate booking kari daie?}"
    ),
    (
        "{Kem cho|Namaste|Hello} {Chef Ji|Bhai|Sir}, "
        "{Tamara kitchen ma|Tamari restaurant ma} daily whole garlic no regular use che? "
        "21st thi ame direct doorstep whole garlic supply start kariye chhiye. "
        "Clean, sorted natural bulbs direct mandi wholesale rate par, ane fakt ₹20 to ₹50 nominal delivery charge ma tamara kitchen par delivery. "
        "{21st na morning slot mate tamaro 10kg/20kg order pre-book kariye?|Tamari restaurant nu name ane address share karsho?}"
    )
]

def resolve_spintax(template: str) -> str:
    """
    Recursively evaluates nested spintax patterns: {option_a|option_b|option_c}.
    Ensures message hash entropy so identical messages are never dispatched.
    """
    pattern = re.compile(r'\{([^{}]+)\}')
    while True:
        match = pattern.search(template)
        if not match:
            break
        options = match.group(1).split('|')
        template = template[:match.start()] + random.choice(options) + template[match.end():]
    return template

def generate_dynamic_outbound_pitch() -> str:
    """
    Selects a base template and compiles high-entropy polymorphic outreach text.
    """
    base = random.choice(SPINTAX_OUTBOUND_TEMPLATES)
    return resolve_spintax(base)
