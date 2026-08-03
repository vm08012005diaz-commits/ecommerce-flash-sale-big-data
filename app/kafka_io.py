import json
import time
from kafka import KafkaProducer
from .config import KAFKA, TOPIC

_producer = None

def producer():
    global _producer
    if _producer is None:
        for attempt in range(20):
            try:
                _producer = KafkaProducer(
                    bootstrap_servers=KAFKA,
                    key_serializer=lambda k: k.encode(),
                    value_serializer=lambda v: json.dumps(v).encode(),
                    acks="all", retries=10, linger_ms=10, compression_type="gzip",
                )
                break
            except Exception:
                if attempt == 19: raise
                time.sleep(2)
    return _producer

def send_events(events):
    p = producer()
    futures = [p.send(TOPIC, key=e["product_id"], value=e) for e in events]
    p.flush(timeout=30)
    for future in futures:
        future.get(timeout=30)

