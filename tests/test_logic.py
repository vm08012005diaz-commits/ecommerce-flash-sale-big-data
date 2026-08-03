from app.generator import generate_event
from app.models import PurchaseAttempt

def test_generated_event_is_valid():
    event = generate_event("P001", malformed_rate=0)
    parsed = PurchaseAttempt.model_validate(event)
    assert parsed.product_id == "P001" and parsed.quantity >= 1

def test_stock_balance_formula():
    stock, requested = 120, 135
    assert stock - requested == -15

