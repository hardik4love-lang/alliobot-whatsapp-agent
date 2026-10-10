import os
import sqlite3
from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import settings

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alliobot.db")

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    """
    Initializes SQLite database schemas for zero-docker native Windows execution.
    """
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        business_name TEXT NOT NULL,
        phone_e164 TEXT UNIQUE NOT NULL,
        contact_person TEXT,
        cuisine_type TEXT,
        surat_suburb TEXT,
        full_address TEXT,
        source TEXT DEFAULT 'SCRAPED',
        status TEXT DEFAULT 'NEW',
        opt_out_timestamp DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        lead_id TEXT NOT NULL REFERENCES leads(id),
        channel TEXT DEFAULT 'WHATSAPP',
        state_machine_current TEXT DEFAULT 'STATE_GREETING',
        last_interaction_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL REFERENCES conversations(id),
        sender_type TEXT,
        message_text TEXT NOT NULL,
        tokens_used INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        lead_id TEXT NOT NULL REFERENCES leads(id),
        order_code TEXT UNIQUE NOT NULL,
        quantity_kg REAL NOT NULL,
        unit_price REAL DEFAULT 120.0,
        total_amount REAL NOT NULL,
        order_status TEXT DEFAULT 'PENDING_DISPATCH',
        delivery_slot TEXT NOT NULL,
        delivery_address TEXT NOT NULL,
        surat_suburb TEXT NOT NULL,
        payment_status TEXT DEFAULT 'UNPAID',
        payment_mode TEXT DEFAULT 'COD_UPI',
        notes TEXT,
        ops_alert_sent INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        delivered_at DATETIME
    );
    """)
    conn.commit()
    conn.close()
    logger.info(f"SQLite database initialized at: {SQLITE_DB_PATH}")

# Initialize on import
init_sqlite_db()
