-- PostgreSQL Schema Initialization for AllioBot (Surat Garlic Sales Agent)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
DO $$ BEGIN
    CREATE TYPE lead_status AS ENUM ('NEW', 'WARMED', 'OUTBOUND_SENT', 'ENGAGED', 'QUALIFIED', 'SAMPLE_SENT', 'CONVERTED', 'DO_NOT_CONTACT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('PENDING_DISPATCH', 'OUT_FOR_DELIVERY', 'DELIVERED', 'PAYMENT_RECEIVED', 'CANCELLED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('UNPAID', 'PAID_UPI', 'PAID_CASH', 'DEFAULTED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 1. Leads Table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(255) NOT NULL,
    phone_e164 VARCHAR(20) UNIQUE NOT NULL,
    contact_person VARCHAR(100),
    cuisine_type VARCHAR(100),
    surat_suburb VARCHAR(100),
    full_address TEXT,
    source VARCHAR(50) DEFAULT 'SCRAPED',
    status lead_status DEFAULT 'NEW',
    opt_out_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone_e164);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_suburb ON leads(surat_suburb);

-- 2. Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    channel VARCHAR(20) DEFAULT 'WHATSAPP',
    state_machine_current VARCHAR(50) DEFAULT 'STATE_GREETING',
    last_interaction_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_conv_lead ON conversations(lead_id);

-- 3. Messages Log Table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(10) CHECK (sender_type IN ('AGENT', 'LEAD', 'SYSTEM')),
    message_text TEXT NOT NULL,
    raw_payload JSONB,
    tokens_used INT DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);

-- 4. Orders Master Table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id),
    order_code VARCHAR(30) UNIQUE NOT NULL,
    quantity_kg NUMERIC(6, 2) NOT NULL,
    unit_price NUMERIC(6, 2) NOT NULL DEFAULT 120.00,
    total_amount NUMERIC(10, 2) NOT NULL,
    order_status order_status DEFAULT 'PENDING_DISPATCH',
    delivery_slot VARCHAR(50) NOT NULL,
    delivery_address TEXT NOT NULL,
    surat_suburb VARCHAR(100) NOT NULL,
    payment_status payment_status DEFAULT 'UNPAID',
    payment_mode VARCHAR(30) DEFAULT 'COD_UPI',
    notes TEXT,
    ops_alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_suburb ON orders(surat_suburb);
