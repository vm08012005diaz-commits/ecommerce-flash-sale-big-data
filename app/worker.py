import json
import time
from datetime import datetime, timezone
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient, UpdateOne
from pydantic import ValidationError
from .config import KAFKA, MONGO, TOPIC, DLQ_TOPIC, DB_NAME, PRODUCTS
from .models import PurchaseAttempt

def run():
    db = MongoClient(MONGO)[DB_NAME]
    db.events.create_index("event_id", unique=True)
    db.products.create_index("product_id", unique=True)
    for p in PRODUCTS:
        db.products.update_one({"product_id": p["id"]}, {"$setOnInsert": {**p, "product_id": p["id"], "attempts": 0, "requested_units": 0, "revenue_exposure": 0}}, upsert=True)
    consumer = KafkaConsumer(TOPIC, bootstrap_servers=KAFKA, group_id="stock-balance-v1", auto_offset_reset="earliest", enable_auto_commit=False, value_deserializer=lambda b: json.loads(b.decode()))
    dlq = KafkaProducer(bootstrap_servers=KAFKA, value_serializer=lambda v: json.dumps(v).encode(), acks="all")
    for msg in consumer:
        raw = msg.value
        try:
            event = PurchaseAttempt.model_validate(raw)
            result = db.events.update_one({"event_id": event.event_id}, {"$setOnInsert": event.model_dump(mode="json")}, upsert=True)
            if result.upserted_id:
                db.products.update_one({"product_id": event.product_id}, {"$inc": {"attempts": 1, "requested_units": event.quantity, "revenue_exposure": event.quantity * event.unit_price}, "$set": {"updated_at": datetime.now(timezone.utc)}})
                db.categories.update_one({"category": event.category}, {"$inc": {"attempts": 1, "requested_units": event.quantity}}, upsert=True)
        except (ValidationError, KeyError, TypeError) as exc:
            dlq.send(DLQ_TOPIC, {"event": raw, "error": str(exc), "failed_at": datetime.now(timezone.utc).isoformat()}).get(timeout=10)
        consumer.commit()

