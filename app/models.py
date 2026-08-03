from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

class PurchaseAttempt(BaseModel):
    event_id: str
    product_id: str
    customer_id: str
    quantity: int = Field(ge=1, le=10)
    unit_price: float = Field(gt=0)
    category: str
    event_time: datetime
    source: str = "flash-sale-web"

    @field_validator("event_time")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

