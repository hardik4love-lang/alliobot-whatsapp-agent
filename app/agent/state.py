from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConversationState(BaseModel):
    lead_id: str
    phone_e164: str
    restaurant_name: Optional[str] = None
    messages: List[Dict[str, str]] = Field(default_factory=list)
    current_intent: str = "INQUIRY"
    extracted_quantity: Optional[float] = None
    extracted_address: Optional[str] = None
    extracted_suburb: Optional[str] = None
    is_sample_request: bool = False
    is_order_confirmed: bool = False
    opted_out: bool = False
