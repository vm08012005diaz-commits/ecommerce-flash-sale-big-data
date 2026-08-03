import random
import uuid
from datetime import datetime, timezone
from .config import PRODUCTS

def generate_event(product_id=None, malformed_rate=0.01, duplicate_id=None):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        product = random.choices(PRODUCTS, weights=[p["weight"] for p in PRODUCTS], k=1)[0]
    event = {
        "event_id": duplicate_id or str(uuid.uuid4()),
        "product_id": product["id"],
        "customer_id": f"C{random.randint(1, 50000):05d}",
        "quantity": random.choices([1, 2, 3, 4, 5], [70, 20, 6, 3, 1], k=1)[0],
        "unit_price": product["price"],
        "category": product["category"],
        "event_time": datetime.now(timezone.utc).isoformat(),
        "source": "flash-sale-web",
    }
    if random.random() < malformed_rate:
        event["quantity"] = -1
    return event

