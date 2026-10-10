import os
from typing import Dict, Any
from loguru import logger
from app.config import settings

class DynamicPricingEngine:
    """
    Cost-Plus Dynamic Pricing Engine for Surat Peeled Garlic.
    Formula: Final Selling Price = Live Mandi Price + Fixed Margin
    Ensures venture margin is locked in regardless of Mandi price oscillations.
    """
    def __init__(self):
        self.live_mandi_price: float = float(os.getenv("LIVE_MANDI_PRICE_PER_KG", 95.00))
        self.fixed_margin: float = float(os.getenv("FIXED_MARGIN_PER_KG", 25.00))
        self.bulk_discount_offset: float = 10.00  # ₹10 discount for 12kg+ bulk daily crates

    def get_current_prices(self) -> Dict[str, Any]:
        standard_price = round(self.live_mandi_price + self.fixed_margin, 2)
        bulk_price = round(max(standard_price - self.bulk_discount_offset, self.live_mandi_price + 15.0), 2)
        return {
            "live_mandi_price": round(self.live_mandi_price, 2),
            "fixed_margin": round(self.fixed_margin, 2),
            "final_standard_price_per_kg": standard_price,
            "final_bulk_price_per_kg": bulk_price,
            "formula": f"Final Price (₹{standard_price:.2f}) = Live Mandi Price (₹{self.live_mandi_price:.2f}) + Fixed Margin (₹{self.fixed_margin:.2f})"
        }

    def update_live_mandi_price(self, new_mandi_price: float) -> Dict[str, Any]:
        self.live_mandi_price = float(new_mandi_price)
        logger.info(f"Live Mandi garlic price updated to ₹{self.live_mandi_price:.2f}/kg.")
        return self.get_current_prices()

    def update_fixed_margin(self, new_margin: float) -> Dict[str, Any]:
        self.fixed_margin = float(new_margin)
        logger.info(f"Fixed venture margin updated to ₹{self.fixed_margin:.2f}/kg.")
        return self.get_current_prices()

pricing_engine = DynamicPricingEngine()
