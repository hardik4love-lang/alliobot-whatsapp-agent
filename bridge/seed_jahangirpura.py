import asyncio
import asyncpg

DATABASE_URL = "postgresql://neondb_owner:npg_e6iVuZDU3IqL@ep-falling-tree-b5b8mc8n-pooler.c-7.us-east-2.aws.neon.tech/neondb"

JAHANGIRPURA_LEADS = [
    {
        "business_name": "Vishala Restaurant & Garden",
        "phone_e164": "+919925626960",
        "cuisine_type": "Kathiyawadi / Multicuisine",
        "surat_suburb": "Jahangirpura",
        "full_address": "Opp. Raj Green Heights, Olpad Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Concord Restaurant & Banquet",
        "phone_e164": "+917779021440",
        "cuisine_type": "Multicuisine / Punjabi",
        "surat_suburb": "Jahangirpura",
        "full_address": "Palanpur Canal Road, Near Morabhagal, Jahangirpura, Surat"
    },
    {
        "business_name": "Concord Kitchen Desk",
        "phone_e164": "+917779049429",
        "cuisine_type": "Multicuisine / Foodservice",
        "surat_suburb": "Jahangirpura",
        "full_address": "Palanpur Canal Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Shree Khodiyar Kathiyawadi Dhaba",
        "phone_e164": "+919714322290",
        "cuisine_type": "Kathiyawadi / Dhaba",
        "surat_suburb": "Jahangirpura",
        "full_address": "5 Square Point, M.V. Circle, Near Anjani Party Plot, Jahangirpura, Surat"
    },
    {
        "business_name": "Maa Matelwali Kathiyawadi Restaurant",
        "phone_e164": "+919601904819",
        "cuisine_type": "Kathiyawadi / Gujarati",
        "surat_suburb": "Jahangirpura",
        "full_address": "Plot No. 24, Olpad Road, Opp. Exiito Commercial Hub, Jahangirpura, Surat"
    },
    {
        "business_name": "Keshav Restaurant",
        "phone_e164": "+918734880106",
        "cuisine_type": "North Indian / Gujarati",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Nandanvan Row House, Olpad Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Roshni Fast Food & Snacks",
        "phone_e164": "+918866689777",
        "cuisine_type": "Fast Food / Quick Bites",
        "surat_suburb": "Jahangirpura",
        "full_address": "Opp. Essar Petrol Pump, Jahangirpura, Surat"
    },
    {
        "business_name": "Helios Pizza Jahangirpura",
        "phone_e164": "+919898413321",
        "cuisine_type": "Pizza / Fast Food",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Cinezza, Dandi Road, Dahin Nagar, Jahangirpura, Surat"
    },
    {
        "business_name": "Helios Pizza Kitchen",
        "phone_e164": "+917600678282",
        "cuisine_type": "Pizza / Fast Food",
        "surat_suburb": "Jahangirpura",
        "full_address": "Dandi Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Madhi Ni Khamni Jahangirpura",
        "phone_e164": "+919824501704",
        "cuisine_type": "Gujarati Farsan & Snacks",
        "surat_suburb": "Jahangirpura",
        "full_address": "B-1, Mahendra Park, Opp. Essar Gas Station, Olpad Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Bhavna Tiffin Service & Cloud Kitchen",
        "phone_e164": "+918511270660",
        "cuisine_type": "Tiffin Service / Cloud Kitchen",
        "surat_suburb": "Jahangirpura",
        "full_address": "H-302, Saipujan Society, Near Ranchhod Park, Jahangirpura, Surat"
    },
    {
        "business_name": "The D Pizza Morabhagal",
        "phone_e164": "+916353446969",
        "cuisine_type": "Pizza / Italian Fast Food",
        "surat_suburb": "Jahangirpura",
        "full_address": "Shop 1, Ground Floor, Blue Eminence, Dandi Road, Morabhagal Circle, Jahangirpura, Surat"
    },
    {
        "business_name": "Street Food Lab",
        "phone_e164": "+919265920655",
        "cuisine_type": "Fast Food / Chaat / Snacks",
        "surat_suburb": "Jahangirpura",
        "full_address": "G5, Blu Eminence, Dandi Road, Opp. Sangini Gardenia, Jahangirpura, Surat"
    },
    {
        "business_name": "Ajay's Cafe Iscon Circle",
        "phone_e164": "+919427071622",
        "cuisine_type": "Fast Food / Cafe",
        "surat_suburb": "Jahangirpura",
        "full_address": "12, Mahendra Park Complex, Near Iscon Circle, Jahangirpura, Surat"
    },
    {
        "business_name": "Ajay's Cafe Jahangirpura Counter",
        "phone_e164": "+917490878037",
        "cuisine_type": "Fast Food / Cafe",
        "surat_suburb": "Jahangirpura",
        "full_address": "Mahendra Park Complex, Jahangirpura, Surat"
    },
    {
        "business_name": "Ajay's Cafe Jahangirabad Canal",
        "phone_e164": "+919724355919",
        "cuisine_type": "Fast Food / Cafe",
        "surat_suburb": "Jahangirpura",
        "full_address": "G-30, Times Galaxy, Near DMart, Canal Road, Jahangirabad / Jahangirpura, Surat"
    },
    {
        "business_name": "Breadliner Savory Kitchen",
        "phone_e164": "+919925417000",
        "cuisine_type": "Bakery / Savory Kitchen",
        "surat_suburb": "Jahangirpura",
        "full_address": "G1-G2 Satyadev Plaza, Iscon Circle, Opp. Jahangirpura Jin, Jahangirpura, Surat"
    },
    {
        "business_name": "La Pino'z Pizza Jahangirpura",
        "phone_e164": "+918758754004",
        "cuisine_type": "Pizza / Italian",
        "surat_suburb": "Jahangirpura",
        "full_address": "Anjani Icon, Chaitrali Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Megh Malhar Dhosa & Fast Food",
        "phone_e164": "+918000862961",
        "cuisine_type": "South Indian / Fast Food",
        "surat_suburb": "Jahangirpura",
        "full_address": "91 Shreedhar Society, Olpad Road, Beside Sagar Dairy, Jahangirpura, Surat"
    },
    {
        "business_name": "Ganesh Kathiyawadi Dhaba",
        "phone_e164": "+919725911065",
        "cuisine_type": "Kathiyawadi / Dhaba",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Dabholi-Jahangirpura Bridge, Causeway Link Road, Surat"
    },
    {
        "business_name": "Bhal Ni Dalbati Dhaba",
        "phone_e164": "+919825129031",
        "cuisine_type": "Rajasthani / Dhaba",
        "surat_suburb": "Jahangirpura",
        "full_address": "Shop 21, Near BRTS Bus Station, Dabholi Road, Jahangirpura, Surat"
    },
    {
        "business_name": "Superia Restaurant & Kitchen",
        "phone_e164": "+919879502211",
        "cuisine_type": "Multicuisine / Punjabi",
        "surat_suburb": "Jahangirpura",
        "full_address": "Exiito Commercial Hub, Olpad-Jahangirpura Main Road, Ranchhod Park, Surat"
    },
    {
        "business_name": "Sanju Dhaba & Tawa Kitchen",
        "phone_e164": "+919712958432",
        "cuisine_type": "Dhaba / Tawa Fry",
        "surat_suburb": "Jahangirpura",
        "full_address": "Tekra Faliya, Near Dabholi-Jahangirpura Bridge, Jahangirpura, Surat"
    },
    {
        "business_name": "Tasty Restaurant & Food Court",
        "phone_e164": "+919904128009",
        "cuisine_type": "North Indian / Chinese",
        "surat_suburb": "Jahangirpura",
        "full_address": "Shubham Complex, Jahangirpura-Olpad Road, Near LPG Pump, Jahangirpura, Surat"
    },
    {
        "business_name": "Annapurna Tiffin & Cloud Kitchen",
        "phone_e164": "+919898243120",
        "cuisine_type": "Tiffin Service / Bhojanalaya",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Variyav Junction, Jahangirabad / Jahangirpura, Surat"
    }
]

async def seed():
    conn = await asyncpg.connect(DATABASE_URL)
    print(f"Connected to Neon DB. Ingesting {len(JAHANGIRPURA_LEADS)} Jahangirpura leads...")
    
    inserted = 0
    updated = 0
    
    for lead in JAHANGIRPURA_LEADS:
        res = await conn.execute("""
            INSERT INTO leads (business_name, phone_e164, cuisine_type, surat_suburb, full_address, source, status)
            VALUES ($1, $2, $3, $4, $5, 'JAHANGIRPURA_HORECA', 'NEW')
            ON CONFLICT (phone_e164) DO UPDATE SET 
                business_name = EXCLUDED.business_name,
                surat_suburb = EXCLUDED.surat_suburb,
                full_address = EXCLUDED.full_address,
                cuisine_type = EXCLUDED.cuisine_type,
                updated_at = NOW();
        """, lead["business_name"], lead["phone_e164"], lead["cuisine_type"], lead["surat_suburb"], lead["full_address"])
        print(f"  {res} -> {lead['business_name']} ({lead['phone_e164']})")
        if "INSERT" in res:
            inserted += 1
        else:
            updated += 1
            
    total = await conn.fetchval("SELECT count(*) FROM leads;")
    j_count = await conn.fetchval("SELECT count(*) FROM leads WHERE surat_suburb = 'Jahangirpura';")
    print(f"\nSeeding complete! Total leads: {total}, Jahangirpura leads: {j_count}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())
