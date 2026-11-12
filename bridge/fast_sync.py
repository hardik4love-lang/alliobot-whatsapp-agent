import asyncio
import asyncpg
import sqlite3
import os
import sys

DATABASE_URL = "postgresql://neondb_owner:npg_e6iVuZDU3IqL@ep-falling-tree-b5b8mc8n-pooler.c-7.us-east-2.aws.neon.tech/neondb"

# Import ALL_150_PROSPECTS from the file or define
from sync_150_database import ALL_150_PROSPECTS

async def fast_sync():
    print("Connecting to Neon DB...", flush=True)
    conn = await asyncpg.connect(DATABASE_URL)
    print("Connected! Initializing table...", flush=True)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS future_clients_and_prospects (
            id SERIAL PRIMARY KEY,
            cluster_code VARCHAR(50) NOT NULL,
            cluster_name VARCHAR(100) NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            phone_e164 VARCHAR(30) UNIQUE NOT NULL,
            cuisine_type VARCHAR(100),
            surat_suburb VARCHAR(100),
            full_address TEXT,
            stage VARCHAR(50) DEFAULT 'PROSPECT',
            priority_rank INT,
            order_unit VARCHAR(20) DEFAULT 'KG',
            min_order_kg NUMERIC(6,2) DEFAULT 1.0,
            delivery_fee_range VARCHAR(50) DEFAULT '₹20 - ₹50',
            launch_scheme_date VARCHAR(50) DEFAULT '21st',
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_fcp_cluster ON future_clients_and_prospects(cluster_code);
        CREATE INDEX IF NOT EXISTS idx_fcp_stage ON future_clients_and_prospects(stage);
        CREATE INDEX IF NOT EXISTS idx_fcp_phone ON future_clients_and_prospects(phone_e164);
        CREATE INDEX IF NOT EXISTS idx_fcp_rank ON future_clients_and_prospects(priority_rank);
    """)

    print(f"Ingesting {len(ALL_150_PROSPECTS)} prospects via fast batch executemany...", flush=True)

    fcp_data = [
        (
            p["cluster_code"], p["cluster_name"], p["business_name"], p["phone_e164"],
            p["cuisine_type"], p["surat_suburb"], p["full_address"], p["priority_rank"],
            "Scheme from 21st, min 1kg+, delivery fee ₹20-₹50"
        )
        for p in ALL_150_PROSPECTS
    ]

    await conn.executemany("""
        INSERT INTO future_clients_and_prospects 
            (cluster_code, cluster_name, business_name, phone_e164, cuisine_type, surat_suburb, full_address, priority_rank, notes)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (phone_e164) DO UPDATE SET
            business_name = EXCLUDED.business_name,
            cluster_code = EXCLUDED.cluster_code,
            cluster_name = EXCLUDED.cluster_name,
            cuisine_type = EXCLUDED.cuisine_type,
            surat_suburb = EXCLUDED.surat_suburb,
            full_address = EXCLUDED.full_address,
            priority_rank = EXCLUDED.priority_rank,
            updated_at = NOW();
    """, fcp_data)

    leads_data = [
        (
            p["business_name"], p["phone_e164"], p["cuisine_type"],
            p["surat_suburb"], p["full_address"]
        )
        for p in ALL_150_PROSPECTS
    ]

    await conn.executemany("""
        INSERT INTO leads (business_name, phone_e164, cuisine_type, surat_suburb, full_address, source, status)
        VALUES ($1, $2, $3, $4, $5, 'NW_SURAT_150_PIPELINE', 'NEW')
        ON CONFLICT (phone_e164) DO UPDATE SET
            business_name = EXCLUDED.business_name,
            cuisine_type = EXCLUDED.cuisine_type,
            surat_suburb = EXCLUDED.surat_suburb,
            full_address = EXCLUDED.full_address,
            updated_at = NOW();
    """, leads_data)

    total_fcp = await conn.fetchval("SELECT count(*) FROM future_clients_and_prospects;")
    total_leads = await conn.fetchval("SELECT count(*) FROM leads;")
    by_cluster = await conn.fetch("SELECT cluster_name, count(*) FROM future_clients_and_prospects GROUP BY cluster_name ORDER BY count DESC;")

    print("\n--- DATABASE SYNC REPORT ---", flush=True)
    print(f" - Total in future_clients_and_prospects: {total_fcp}", flush=True)
    print(f" - Total in active bot leads table: {total_leads}", flush=True)
    for bc in by_cluster:
        print(f"   * {bc['cluster_name']}: {bc['count']} prospects", flush=True)

    await conn.close()

    # Mirror to SQLite local database
    local_db_path = "C:/Users/om/.gemini/antigravity/scratch/alliobot-whatsapp-agent/database/future_clients_and_prospects.db"
    os.makedirs(os.path.dirname(local_db_path), exist_ok=True)
    sl_conn = sqlite3.connect(local_db_path)
    sl_cur = sl_conn.cursor()
    sl_cur.execute("""
        CREATE TABLE IF NOT EXISTS future_clients_and_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_code TEXT,
            cluster_name TEXT,
            business_name TEXT,
            phone_e164 TEXT UNIQUE,
            cuisine_type TEXT,
            surat_suburb TEXT,
            full_address TEXT,
            stage TEXT DEFAULT 'PROSPECT',
            priority_rank INTEGER,
            order_unit TEXT DEFAULT 'KG',
            min_order_kg REAL DEFAULT 1.0,
            delivery_fee_range TEXT DEFAULT '₹20 - ₹50',
            launch_scheme_date TEXT DEFAULT '21st',
            notes TEXT
        );
    """)
    sl_cur.executemany("""
        INSERT OR REPLACE INTO future_clients_and_prospects 
        (cluster_code, cluster_name, business_name, phone_e164, cuisine_type, surat_suburb, full_address, priority_rank, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [(p["cluster_code"], p["cluster_name"], p["business_name"], p["phone_e164"], p["cuisine_type"], p["surat_suburb"], p["full_address"], p["priority_rank"], "Scheme from 21st, min 1kg+, delivery fee ₹20-₹50") for p in ALL_150_PROSPECTS])
    sl_conn.commit()
    sl_conn.close()
    print(f"Local SQLite database mirrored at: {local_db_path}", flush=True)

if __name__ == "__main__":
    asyncio.run(fast_sync())
