from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum

class OrderType(str, Enum):
    SAMPLE_500G = "SAMPLE_500G"
    COMMERCIAL_ORDER = "COMMERCIAL_ORDER"

class DeliverySlot(str, Enum):
    MORNING_PREP = "05:00 - 08:00 AM"
    EVENING_PREP = "02:00 - 04:30 PM"

class ParsedOrder(BaseModel):
    restaurant_name: str = Field(description="Name of restaurant or kitchen")
    quantity_kg: float = Field(description="Quantity in kilograms")
    unit_price: float = Field(default=120.0, description="Unit price per kg in INR")
    delivery_address: str = Field(description="Address and landmark")
    surat_suburb: str = Field(default="Surat", description="Locality e.g. Piplod, Adajan, Vesu, Varachha")
    delivery_slot: DeliverySlot = Field(default=DeliverySlot.MORNING_PREP)
    payment_mode: str = Field(default="COD_UPI", description="COD_UPI or E_NACH")
    order_type: OrderType = Field(default=OrderType.COMMERCIAL_ORDER)

    @property
    def total_amount(self) -> float:
        if self.order_type == OrderType.SAMPLE_500G:
            return 0.0
        return round(self.quantity_kg * self.unit_price, 2)
