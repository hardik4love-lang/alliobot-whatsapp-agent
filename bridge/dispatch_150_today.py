import asyncio
import asyncpg
import requests
import random
import re
import sys

DATABASE_URL = "postgresql://neondb_owner:npg_e6iVuZDU3IqL@ep-falling-tree-b5b8mc8n-pooler.c-7.us-east-2.aws.neon.tech/neondb"
RENDER_URL = "https://alliobot-whatsapp-agent.onrender.com"

# Ultra-short, simple, unbranded templates in Gujarati and Hindi
SPINTAX_TEMPLATES = [
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

def generate_pitch() -> str:
    return resolve_spintax(random.choice(SPINTAX_TEMPLATES))

async def run_full_150_dispatch():
    conn = await asyncpg.connect(DATABASE_URL)
    print("Connected to Neon DB. Loading all pending prospects for today...", flush=True)

    prospects = await conn.fetch("""
        SELECT id, cluster_name, business_name, phone_e164, cuisine_type, full_address, priority_rank
        FROM future_clients_and_prospects
        WHERE stage = 'PROSPECT'
        ORDER BY priority_rank ASC;
    """)

    total_prospects = len(prospects)
    print(f"Total pending prospects loaded: {total_prospects} (Target: 150)", flush=True)

    if total_prospects == 0:
        print("All prospects have already been contacted!", flush=True)
        await conn.close()
        return

    sent_count = 0
    for idx, p in enumerate(prospects, start=1):
        phone = p["phone_e164"]
        name = p["business_name"]
        cluster = p["cluster_name"]
        pitch = generate_pitch()

        clean_number = phone.replace("+", "").strip()
        print(f"\n[{idx}/{total_prospects}] [{cluster}] Sending to {name} ({phone})...", flush=True)

        try:
            resp = requests.post(
                f"{RENDER_URL}/message/sendText",
                json={"number": clean_number, "text": pitch},
                timeout=20
            )

            if resp.status_code == 200:
                sent_count += 1
                await conn.execute("""
                    UPDATE future_clients_and_prospects
                    SET stage = 'CONTACTED', updated_at = NOW()
                    WHERE id = $1;
                """, p["id"])

                await conn.execute("""
                    UPDATE leads
                    SET status = 'OUTBOUND_SENT', updated_at = NOW()
                    WHERE phone_e164 = $1;
                """, phone)

                # Ensure conversation and message are recorded
                lead_id = await conn.fetchval("SELECT id FROM leads WHERE phone_e164 = $1 LIMIT 1;", phone)
                if lead_id:
                    conv_id = await conn.fetchval("""
                        SELECT id FROM conversations WHERE lead_id = $1 LIMIT 1;
                    """, lead_id)
                    if not conv_id:
                        conv_id = await conn.fetchval("""
                            INSERT INTO conversations (lead_id) VALUES ($1) RETURNING id;
                        """, lead_id)
                    if conv_id:
                        await conn.execute("""
                            INSERT INTO messages (conversation_id, sender_type, message_text)
                            VALUES ($1, 'AGENT', $2);
                        """, conv_id, pitch)

                print(f"  -> SUCCESS! Dispatched to {name}. Total sent today: {sent_count}", flush=True)
            else:
                print(f"  -> Gateway error ({resp.status_code}): {resp.text}", flush=True)

        except Exception as err:
            print(f"  -> Network error sending to {phone}: {err}", flush=True)

        # Anti-ban pacing: 25 per hour = 1 message every 120 to 168 seconds
        if idx < total_prospects:
            jitter = random.uniform(120.0, 168.0)
            print(f"  Pacing: Waiting {jitter:.1f}s before next contact (~25/hour rate)...", flush=True)
            await asyncio.sleep(jitter)

    print(f"\n=============================================", flush=True)
    print(f"Campaign Complete! Dispatched {sent_count} / {total_prospects} prospects today.", flush=True)
    print(f"=============================================", flush=True)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run_full_150_dispatch())
