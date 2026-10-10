import uuid
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from loguru import logger
import psycopg2
from psycopg2.extras import RealDictCursor
import redis

from app.config import settings
from app.lead_engine.scraper import scrape_surat_food_amenities
from app.compliance.jitter import is_within_circadian_window, calculate_poisson_jitter_delay
from app.compliance.entropy import generate_dynamic_outbound_pitch
from app.compliance.presence import simulate_human_presence_and_send
from app.agent.orchestrator import generate_sales_response
from app.orders.extractor import extract_order_from_text
from app.alerts.group_notifier import dispatch_operations_group_alert

app = FastAPI(
    title="AllioBot WhatsApp Sales Agent",
    version="1.0.0",
    description="Zero-Cost WhatsApp Sales Agent for B2B Peeled Garlic in Surat"
)

# Redis connection for deduplication and rate-limiting
try:
    r_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis initialization warning: {e}")
    r_client = None

def get_db_connection():
    return psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "primary_phone": settings.USER_PHONE_NUMBER,
        "max_outbound_daily": settings.MAX_OUTBOUND_PER_DAY,
        "operations_group": settings.OPERATIONS_GROUP_JID
    }

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming WhatsApp Webhooks from self-hosted Evolution API.
    Processes incoming customer messages, triggers LLM conversational agent,
    and extracts structured orders for operations alert.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event = data.get("event")
    if event != "messages.upsert":
        return {"status": "ignored_event", "event": event}

    message_data = data.get("data", {})
    key = message_data.get("key", {})

    # Ignore messages sent by ourselves
    if key.get("fromMe", False):
        return {"status": "ignored_self"}

    sender_jid = key.get("remoteJid", "")
    # Ignore group messages in the sales receiver
    if "@g.us" in sender_jid:
        return {"status": "ignored_group"}

    customer_phone = "+" + sender_jid.split("@")[0]
    message_text = (
        message_data.get("message", {}).get("conversation")
        or message_data.get("message", {}).get("extendedTextMessage", {}).get("text")
        or ""
    ).strip()

    message_id = key.get("id")
    if not message_text or not message_id:
        return {"status": "ignored_empty"}

    # Idempotency check via Redis (6-hour window)
    if r_client:
        if r_client.get(f"seen_msg:{message_id}"):
            return {"status": "already_processed"}
        r_client.setex(f"seen_msg:{message_id}", 21600, "1")

    logger.info(f"Received message from {customer_phone}: '{message_text}'")

    background_tasks.add_task(
        process_incoming_conversation,
        customer_phone=customer_phone,
        incoming_text=message_text
    )

    return {"status": "accepted"}

async def process_incoming_conversation(customer_phone: str, incoming_text: str):
    """
    Asynchronously processes the conversation:
    1. Looks up or creates lead and conversation in PostgreSQL
    2. Runs Ollama Qwen-2.5 conversational agent
    3. Simulates human presence and sends response via Evolution API
    4. Evaluates whether an order or sample was confirmed
    5. Dispatches formatted alert to Internal Operations WhatsApp Group
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get or create lead
        cur.execute(
            """
            INSERT INTO leads (business_name, phone_e164, status)
            VALUES (%s, %s, 'ENGAGED')
            ON CONFLICT (phone_e164) DO UPDATE SET updated_at = NOW()
            RETURNING id;
            """,
            ("Inbound Lead", customer_phone)
        )
        lead_row = cur.fetchone()
        lead_id = lead_row["id"]

        # Get or create conversation
        cur.execute(
            """
            SELECT id FROM conversations WHERE lead_id = %s AND is_active = TRUE LIMIT 1;
            """,
            (lead_id,)
        )
        conv_row = cur.fetchone()
        if not conv_row:
            cur.execute(
                """
                INSERT INTO conversations (lead_id) VALUES (%s) RETURNING id;
                """,
                (lead_id,)
            )
            conv_row = cur.fetchone()
        conversation_id = conv_row["id"]

        # Record incoming message
        cur.execute(
            """
            INSERT INTO messages (conversation_id, sender_type, message_text)
            VALUES (%s, 'LEAD', %s);
            """,
            (conversation_id, incoming_text)
        )
        conn.commit()

        # Retrieve recent history
        cur.execute(
            """
            SELECT sender_type, message_text FROM messages
            WHERE conversation_id = %s ORDER BY timestamp ASC LIMIT 8;
            """,
            (conversation_id,)
        )
        history_rows = cur.fetchall()
        history = [
            {"role": "assistant" if r["sender_type"] == "AGENT" else "user", "content": r["message_text"]}
            for r in history_rows
        ]

        # Generate LLM response
        bot_reply = await generate_sales_response(history, incoming_text)

        # Send via Evolution API with human presence mimicry
        await simulate_human_presence_and_send(customer_phone, bot_reply)

        # Record outbound response
        cur.execute(
            """
            INSERT INTO messages (conversation_id, sender_type, message_text)
            VALUES (%s, 'AGENT', %s);
            """,
            (conversation_id, bot_reply)
        )
        conn.commit()

        # Check for order extraction
        full_transcript = "\n".join([f"{h['role']}: {h['content']}" for h in history] + [f"assistant: {bot_reply}"])
        parsed_order = await extract_order_from_text(full_transcript)

        if parsed_order:
            order_code = f"ORD-{uuid.uuid4().hex[:6].upper()}"
            cur.execute(
                """
                INSERT INTO orders (
                    lead_id, order_code, quantity_kg, unit_price, total_amount,
                    delivery_slot, delivery_address, surat_suburb, payment_mode
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    lead_id, order_code, parsed_order.quantity_kg, parsed_order.unit_price,
                    parsed_order.total_amount, parsed_order.delivery_slot.value,
                    parsed_order.delivery_address, parsed_order.surat_suburb, parsed_order.payment_mode
                )
            )
            conn.commit()
            logger.info(f"Order created {order_code} for {customer_phone}. Dispatching Operations WhatsApp Group Alert...")

            # Alert Internal Operations WhatsApp Group
            await dispatch_operations_group_alert(parsed_order, customer_phone, order_code)

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in conversation processing pipeline: {e}")

@app.post("/leads/scrape")
async def trigger_lead_scrape(background_tasks: BackgroundTasks):
    """
    Triggers OpenStreetMap lead scraping across Surat and stores unique leads in PostgreSQL.
    """
    def task():
        leads = scrape_surat_food_amenities()
        if not leads:
            return
        conn = get_db_connection()
        cur = conn.cursor()
        inserted = 0
        for ld in leads:
            try:
                cur.execute(
                    """
                    INSERT INTO leads (business_name, phone_e164, cuisine_type, surat_suburb, full_address, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (phone_e164) DO NOTHING;
                    """,
                    (ld["business_name"], ld["phone_e164"], ld["cuisine_type"], ld["surat_suburb"], ld["full_address"], ld["source"])
                )
                inserted += cur.rowcount
            except Exception:
                pass
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Scraped and inserted {inserted} new unique leads into PostgreSQL.")

    background_tasks.add_task(task)
    return {"status": "scraping_started", "source": "OpenStreetMap_Surat"}

@app.post("/leads/dispatch-outbound")
async def trigger_safe_outbound_batch(background_tasks: BackgroundTasks):
    """
    Executes a safe single-number outbound batch (max 25 leads/day)
    with Poisson jitter and circadian gating.
    """
    if not is_within_circadian_window():
        return {
            "status": "halted_by_circadian_gate",
            "message": "Outbound allowed only during 09:30-11:30 AM and 03:30-05:30 PM IST to protect phone reputation."
        }

    async def outbound_worker():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, phone_e164, business_name FROM leads
            WHERE status = 'NEW' LIMIT %s;
            """,
            (settings.MAX_OUTBOUND_PER_DAY,)
        )
        leads_to_contact = cur.fetchall()
        cur.close()
        conn.close()

        logger.info(f"Starting single-number safe outbound for {len(leads_to_contact)} leads...")
        for ld in leads_to_contact:
            pitch_text = generate_dynamic_outbound_pitch()
            phone = ld["phone_e164"]

            success = await simulate_human_presence_and_send(phone, pitch_text)
            if success:
                conn_up = get_db_connection()
                cur_up = conn_up.cursor()
                cur_up.execute("UPDATE leads SET status = 'OUTBOUND_SENT', updated_at = NOW() WHERE id = %s;", (ld["id"],))
                conn_up.commit()
                cur_up.close()
                conn_up.close()

            # Poisson jitter delay before next contact
            delay = calculate_poisson_jitter_delay()
            logger.info(f"Waiting {delay:.1f}s before next contact to keep single number safe...")
            await asyncio.sleep(delay)

    background_tasks.add_task(outbound_worker)
    return {"status": "outbound_worker_launched", "batch_limit": settings.MAX_OUTBOUND_PER_DAY}
