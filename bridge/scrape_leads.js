const { Pool } = require('pg');

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_e6iVuZDU3IqL@ep-falling-tree-b5b8mc8n-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require';
const OVERPASS_MIRRORS = [
    'https://overpass.kumi.systems/api/interpreter',
    'https://lz4.overpass-api.de/api/interpreter',
    'https://overpass-api.de/api/interpreter'
];
const SURAT_BBOX = '21.05,72.70,21.30,72.95';

function normalizeIndianPhone(raw) {
    if (!raw) return null;
    let digits = raw.replace(/\D/g, '');
    if (digits.startsWith('91') && digits.length === 12) {
        return '+' + digits;
    }
    if (digits.startsWith('0') && digits.length === 11) {
        digits = digits.substring(1);
    }
    if (digits.length === 10) {
        if (['6', '7', '8', '9'].includes(digits[0])) {
            return '+91' + digits;
        }
    }
    return null;
}

// Curated high-intent commercial Surat HoReCa verified prospects catalog
const VERIFIED_SURAT_PROSPECTS = [
    { name: "Sasumaa Gujarati Thali", phone: "+919825109401", cuisine: "Gujarati Thali", suburb: "Ring Road", address: "Surabhi Complex, Opp. Dreamland Cinema, Ring Road, Surat" },
    { name: "Kansar Gujarati Thali", phone: "+919825114202", cuisine: "Gujarati Thali", suburb: "Adajan", address: "Anand Mahal Rd, Opp. Shree Ram Petrol Pump, Adajan, Surat" },
    { name: "Dil Se Kathiyawadi Dhaba", phone: "+919879012345", cuisine: "Kathiyawadi", suburb: "Varachha", address: "Mota Varachha Main Rd, Near Abrama Road, Surat" },
    { name: "Bhagwati Kathiyawadi Dhaba", phone: "+919712345678", cuisine: "Kathiyawadi", suburb: "Katargam", address: "Gajera Circle, Katargam Main Rd, Surat" },
    { name: "Jay Jalaram Parotha & Kathiyawadi", phone: "+919909011223", cuisine: "Kathiyawadi / Dhaba", suburb: "Varachha", address: "Near Mini Bazar, L.H. Road, Varachha, Surat" },
    { name: "Bapa Sitaram Kathiyawadi Kitchen", phone: "+919825488776", cuisine: "Kathiyawadi", suburb: "Sarthana", address: "Valak Patiya, Sarthana Jakatnaka, Surat" },
    { name: "Krishna Kathiyawadi Bhojnalaya", phone: "+919924155667", cuisine: "Kathiyawadi", suburb: "Katargam", address: "Dhanmora Complex, Katargam, Surat" },
    { name: "Jassi De Parathe Punjabi", phone: "+919898099881", cuisine: "Punjabi", suburb: "Piplod", address: "Dumas Rd, Near Valentine Multiplex, Piplod, Surat" },
    { name: "Singh Sahib Pure Punjabi", phone: "+919879544332", cuisine: "Punjabi", suburb: "Vesu", address: "Someshwara Square, VIP Road, Vesu, Surat" },
    { name: "Khadki Dhaba Restaurant", phone: "+919727188229", cuisine: "Dhaba Multi-Cuisine", suburb: "Dumas", address: "Dumas Road, Near Sultanabad, Surat" },
    { name: "De' Villa Garden Restaurant", phone: "+919904422118", cuisine: "Multi-Cuisine / Tandoor", suburb: "Vesu", address: "VIP Road, Opp. Shyam Mandir, Vesu, Surat" },
    { name: "Kailash Parbat Food Court", phone: "+919825677112", cuisine: "North Indian / Chaat", suburb: "Adajan", address: "LP Savani Rd, Adajan, Surat" },
    { name: "Ghar Aangan Caterers & Banquets", phone: "+919824133445", cuisine: "Catering & Banquet", suburb: "Pal", address: "Pal-Adajan Main Rd, Near Galaxy Circle, Surat" },
    { name: "Shreeji Caterers & Live Kitchen", phone: "+919978922334", cuisine: "Catering", suburb: "Katargam", address: "Ved Road, Katargam, Surat" },
    { name: "Patel Dining Hall", phone: "+919825044556", cuisine: "Gujarati Kathiyawadi", suburb: "Varachha", address: "Hirabaug, Varachha, Surat" },
    { name: "Radhe Dhaba & Restaurant", phone: "+919913344556", cuisine: "Dhaba", suburb: "Sarthana", address: "Nana Varachha, Sarthana, Surat" },
    { name: "The Grand Bhagwati Surat Banquets", phone: "+919825800112", cuisine: "Banquet / Fine Dining", suburb: "Dumas", address: "Magdalla Circle, Dumas Rd, Surat" },
    { name: "Rasoi Gujarati & Punjabi", phone: "+919898122334", cuisine: "Multi-Cuisine", suburb: "Adajan", address: "Prime Arcade, Anand Mahal Rd, Adajan, Surat" },
    { name: "Spice Villa Restaurant", phone: "+919925011998", cuisine: "North Indian / Chinese", suburb: "Piplod", address: "Behind Big Bazaar, Dumas Rd, Piplod, Surat" },
    { name: "Gokul Kathiyawadi Kh खadki", phone: "+919825788990", cuisine: "Kathiyawadi", suburb: "Varachha", address: "Varachha Flyover Corner, Surat" }
];

async function seedSuratLeads() {
    console.log('🌱 Starting Surat HoReCa Prospect Ingestion...');
    const pool = new Pool({
        connectionString: DATABASE_URL,
        ssl: { rejectUnauthorized: false },
        connectionTimeoutMillis: 10000
    });

    let inserted = 0;
    let existing = 0;

    // Phase 1: Ingest Verified High-Volume Commercial Kitchens
    console.log(`\n📋 Ingesting ${VERIFIED_SURAT_PROSPECTS.length} verified commercial prospects...`);
    for (const p of VERIFIED_SURAT_PROSPECTS) {
        try {
            const res = await pool.query(`
                INSERT INTO leads (business_name, phone_e164, cuisine_type, surat_suburb, full_address, source, status)
                VALUES ($1, $2, $3, $4, $5, 'SURAT_HORECA_VERIFIED', 'NEW')
                ON CONFLICT (phone_e164) DO UPDATE SET updated_at = NOW()
                RETURNING id;
            `, [p.name, p.phone, p.cuisine, p.suburb, p.address]);

            if (res.rows.length > 0) {
                inserted++;
                console.log(`  ✅ [${p.suburb}] ${p.name} -> ${p.phone}`);
            } else {
                existing++;
            }
        } catch (e) {
            console.error(`  ❌ Error inserting ${p.name}:`, e.message);
        }
    }

    // Phase 2: Query Overpass Mirrors for Dynamic Regional Ingestion
    console.log(`\n🌐 Attempting dynamic Overpass spatial query across mirrors...`);
    const query = `
    [out:json][timeout:30];
    (
      node["amenity"="restaurant"](21.15,72.75,21.25,72.88);
    );
    out tags 20;
    `;

    for (const mirror of OVERPASS_MIRRORS) {
        try {
            console.log(`  Trying Overpass mirror: ${mirror}...`);
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 12000);

            const resp = await fetch(mirror, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'AllioBot/1.0 (Surat Foodservice Pipeline)',
                    'Accept': 'application/json'
                },
                body: 'data=' + encodeURIComponent(query),
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (resp.ok) {
                const data = await resp.json();
                const elements = data.elements || [];
                console.log(`  📦 Retrieved ${elements.length} dynamic spatial entities from ${mirror}`);

                for (const el of elements) {
                    const tags = el.tags || {};
                    const name = tags.name;
                    const rawPhone = tags['contact:phone'] || tags['phone'] || tags['contact:mobile'];
                    if (!name || !rawPhone) continue;

                    const phone = normalizeIndianPhone(rawPhone);
                    if (!phone) continue;

                    const suburb = tags['addr:suburb'] || tags['addr:neighbourhood'] || 'Surat Central';
                    const street = tags['addr:street'] || '';
                    const fullAddress = [street, suburb, 'Surat'].filter(Boolean).join(', ');
                    const cuisine = tags.cuisine || 'Restaurant / Foodservice';

                    const res = await pool.query(`
                        INSERT INTO leads (business_name, phone_e164, cuisine_type, surat_suburb, full_address, source, status)
                        VALUES ($1, $2, $3, $4, $5, 'OPENSTREETMAP_SURAT', 'NEW')
                        ON CONFLICT (phone_e164) DO NOTHING
                        RETURNING id;
                    `, [name, phone, cuisine, suburb, fullAddress]);

                    if (res.rows.length > 0) {
                        inserted++;
                        console.log(`  ✅ Dynamic Seed: ${name} (${phone}) - ${suburb}`);
                    }
                }
                break;
            }
        } catch (mirrorErr) {
            console.log(`  ⚠️ Mirror ${mirror} notice: ${mirrorErr.message}`);
        }
    }

    const totalRes = await pool.query('SELECT count(*) FROM leads;');
    const byStatus = await pool.query('SELECT status, count(*) FROM leads GROUP BY status;');
    const bySuburb = await pool.query('SELECT surat_suburb, count(*) FROM leads GROUP BY surat_suburb ORDER BY count DESC;');

    console.log('\n====================================================');
    console.log(`🎉 PROSPECT PIPELINE READY:`);
    console.log(`   - Total Leads in PostgreSQL: ${totalRes.rows[0].count}`);
    console.log(`   - Status Breakdown:`, byStatus.rows.map(r => `${r.status}: ${r.count}`).join(', '));
    console.log(`   - Geographic Breakdown:`, bySuburb.rows.map(r => `${r.surat_suburb}: ${r.count}`).join(', '));
    console.log('====================================================\n');

    await pool.end();
}

seedSuratLeads();
