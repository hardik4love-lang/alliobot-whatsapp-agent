import asyncio
from datetime import datetime
from loguru import logger
from app.config import settings
from app.db_adapter import db
from app.compliance.presence import simulate_human_presence_and_send

async def evaluate_reorder_triggers():
    """
    Evaluates customer inventory depletion cycles and dispatches
    one-tap reorder prompts in authentic Kathiyawadi/Hinglish dialect.
    Targeted at 03:30 PM IST (when chefs assess evening prep and tomorrow morning inventory).
    """
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # Query leads whose last order was placed 48 hours ago
        query = db.format_query("""
            SELECT l.id, l.phone_e164, l.business_name,
                   o.quantity_kg, o.delivery_slot, o.surat_suburb
            FROM leads l
            JOIN orders o ON l.id = o.lead_id
            WHERE o.created_at <= NOW() - INTERVAL '48 hours'
            ORDER BY o.created_at DESC
            LIMIT 30;
        """)
        cur.execute(query)
        leads_to_nurture = cur.fetchall()

        logger.info(f"Evaluating replenishment triggers for {len(leads_to_nurture)} accounts...")

        for row in leads_to_nurture:
            phone = row["phone_e164"] if isinstance(row, dict) else row[1]
            biz_name = row["business_name"] if isinstance(row, dict) else row[2]
            qty = float(row["quantity_kg"] if isinstance(row, dict) else row[3])
            slot = row["delivery_slot"] if isinstance(row, dict) else row[4]

            # Friction-free single-word replenishment prompt
            prompt_msg = (
                f"Kem cho Chef! {biz_name} ma kale morning prep mate garlic crate replenish karvu che? "
                f"Same {int(qty)}kg crate kal savare 06:00 AM slot schedule kari daiye? "
                f"Fakt 'Ha' lakhi ne reply aapo."
            )

            await simulate_human_presence_and_send(phone, prompt_msg)
            await asyncio.sleep(15)  # Safe spacing between reminders

    except Exception as e:
        logger.error(f"Error evaluating replenishment triggers: {e}")
    finally:
        cur.close()
        conn.close()
