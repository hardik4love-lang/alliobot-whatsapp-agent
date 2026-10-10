import random
import re

SPINTAX_OUTBOUND_TEMPLATES = [
    (
        "{Kem cho|Namaste|Pranam} {Bhai|Chef|Owner|Ji}, "
        "{Tamari kitchen ma|Tamare restaurant ma|Kitchen prep mate} garlic no daily use che? "
        "Ame Surat ma 100% {sukhu ane saaf|dry pneumatic peeled|ready-to-use} lahsan "
        "{pure ₹120/kg ma|wholesale ₹120 rate ma|fakt ₹120 rate ma} direct deliver kariye chhiye. "
        "{Kale morning mate ek 500g trial sample mocklavu?|Aje ek sample try karsho?|Quality check mate ek free sample joyiye?}"
    ),
    (
        "{Namaste|Hello|Kem cho} {Ji|Bhai|Chef}, "
        "{VedicAllio Surat thi contact karu chhu|Surat fresh peeled garlic supply taraf thi}. "
        "{Tamara restaurant ma|Tamari kitchen ma} market karta saari quality nu "
        "dry peeled lahsan ₹120/kg ma provide kariye chhiye (zero water, no slime). "
        "{Tamara chef mate ek trial sample drop kariye kale?|Sample pack try karvu che kal sakale?}"
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
