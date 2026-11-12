import random
import re

SPINTAX_OUTBOUND_TEMPLATES = [
    (
        "{નમસ્તે|કેમ છો|પ્રણામ} {ભાઈ|શેફ જી}, "
        "અમે સુરતમાં તમારા કિચને સીધું દેશી આખું લસણ પહોંચાડીએ છીએ (૧ kg પણ મળી જશે). "
        "૨૧ તારીખથી નવી ડોરસ્ટેપ સર્વિસ શરૂ છે. ભાવ અને વિગત મોકલું?"
    ),
    (
        "{નમસ્તે|કેમ છો} {શેફ|ભાઈ}, "
        "૨૧ તારીખથી તમારા કિચન પર સીધું આખું દેશી લસણ ડિલિવરી મળશે — ૧ kg થી પણ મંગાવી શકો છો, APMC જવાની જરૂર નથી. "
        "રેટ અને ડિટેઇલ મોકલું?"
    ),
    (
        "{नमस्ते|प्रणाम|हेलो} {शेफ जी|भाई}, "
        "21 तारीख से आपके किचन पर सीधा साबुत देसी लहसुन पहुंचा रहे हैं (1 kg भी मिल जाएगा). "
        "मंडी जाने की झंझट नहीं. रेट और डिटेल भेजूं?"
    )
]

def resolve_spintax(template: str) -> str:
    pattern = re.compile(r'\{([^{}]+)\}')
    while True:
        match = pattern.search(template)
        if not match:
            break
        options = match.group(1).split('|')
        template = template[:match.start()] + random.choice(options) + template[match.end():]
    return template

def generate_dynamic_outbound_pitch() -> str:
    base = random.choice(SPINTAX_OUTBOUND_TEMPLATES)
    return resolve_spintax(base)
