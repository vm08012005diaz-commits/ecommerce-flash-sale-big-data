import os

KAFKA = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
MONGO = os.getenv("MONGO_URI", "mongodb://localhost:27017")
TOPIC = os.getenv("KAFKA_TOPIC", "purchase-attempts")
DLQ_TOPIC = os.getenv("KAFKA_DLQ_TOPIC", "purchase-attempts-dlq")
DB_NAME = "flash_sale"

PRODUCTS = [
    {"id": "P001", "name": "Smartphone X", "category": "Electrónica", "price": 899.99, "stock": 120, "weight": 35},
    {"id": "P002", "name": "Audífonos Pro", "category": "Electrónica", "price": 149.99, "stock": 300, "weight": 25},
    {"id": "P003", "name": "Tenis Urban", "category": "Moda", "price": 79.99, "stock": 220, "weight": 16},
    {"id": "P004", "name": "Cafetera Smart", "category": "Hogar", "price": 119.99, "stock": 90, "weight": 10},
    {"id": "P005", "name": "Libro Big Data", "category": "Libros", "price": 39.99, "stock": 180, "weight": 6},
    {"id": "P006", "name": "Reloj Fit", "category": "Deportes", "price": 69.99, "stock": 140, "weight": 8},
]

