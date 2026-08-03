import os
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from .config import MONGO, DB_NAME, PRODUCTS
from .generator import generate_event
from .kafka_io import send_events

app = FastAPI(title="Flash Sale Big Data", version="1.0")

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/products")
def products(): return PRODUCTS

@app.post("/api/send/{product_id}")
def send_one(product_id: str):
    if not any(p["id"] == product_id for p in PRODUCTS): raise HTTPException(404, "Producto no encontrado")
    event = generate_event(product_id, malformed_rate=0)
    send_events([event])
    return {"sent": 1, "event": event}

@app.post("/api/burst")
def burst(count: int = Query(1000, ge=1, le=100000), malformed_rate: float = Query(0.01, ge=0, le=.2), duplicate_rate: float = Query(0.01, ge=0, le=.2)):
    start = time.perf_counter(); events=[]; previous=None
    for _ in range(count):
        duplicate = previous["event_id"] if previous and __import__('random').random() < duplicate_rate else None
        event = generate_event(malformed_rate=malformed_rate, duplicate_id=duplicate); events.append(event); previous=event
    send_events(events); elapsed=time.perf_counter()-start
    return {"sent": count, "seconds": round(elapsed,3), "throughput_events_sec": round(count/elapsed,2)}

@app.get("/api/dashboard")
def dashboard():
    docs=list(MongoClient(MONGO)[DB_NAME].products.find({}, {"_id":0}).sort("requested_units",-1))
    for d in docs:
        d["balance"] = d.get("stock",0)-d.get("requested_units",0)
        d["status"] = "SOBREVENTA" if d["balance"] < 0 else ("CRÍTICO" if d["balance"] <= d.get("stock",0)*.2 else "DISPONIBLE")
        if "updated_at" in d: d["updated_at"] = d["updated_at"].isoformat()
    return docs

HTML='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Flash Sale Control</title><style>
body{font-family:system-ui;background:#08111f;color:#eaf0ff;margin:0}main{max-width:1100px;margin:auto;padding:30px}.top{display:flex;justify-content:space-between;align-items:center}.card{background:#111e32;border:1px solid #263a57;border-radius:16px;padding:18px;margin:14px 0}button,select,input{padding:11px;border-radius:9px;border:0;margin:4px}button{background:#6c63ff;color:white;font-weight:700;cursor:pointer}.burst{background:#ff4d6d}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:11px;border-bottom:1px solid #263a57}.ok{color:#62dca5}.bad{color:#ff6b81}.warn{color:#ffd166}.metric{font-size:2rem;font-weight:800}small{color:#9fb0c8}@media(max-width:700px){table{font-size:12px}.hide{display:none}}
</style></head><body><main><div class="top"><div><h1>⚡ Flash Sale Control</h1><small>Balance de stock en tiempo real</small></div><div id="total" class="metric">0</div></div>
<div class="card"><h3>Generador de eventos</h3><select id="product"></select><button onclick="one()">Enviar intento individual</button><input id="count" type="number" value="1000" min="1" max="100000"><button class="burst" onclick="burst()">Disparar pico masivo</button><p id="result"></p></div>
<div class="card"><h3>Inventario e intentos</h3><table><thead><tr><th>Producto</th><th>Categoría</th><th>Stock</th><th>Intentos</th><th>Unidades solicitadas</th><th>Balance</th><th>Estado</th><th class="hide">Exposición</th></tr></thead><tbody id="rows"></tbody></table></div></main><script>
async function init(){let p=await(await fetch('/api/products')).json();product.innerHTML=p.map(x=>`<option value="${x.id}">${x.id} · ${x.name}</option>`).join(''); refresh();setInterval(refresh,2000)}
async function one(){result.textContent='Enviando...';let r=await(await fetch('/api/send/'+product.value,{method:'POST'})).json();result.textContent='Evento enviado: '+r.event.event_id}
async function burst(){result.textContent='Generando y enviando pico...';let n=count.value;let r=await(await fetch('/api/burst?count='+n,{method:'POST'})).json();result.textContent=`${r.sent} eventos en ${r.seconds}s · ${r.throughput_events_sec} eventos/s`}
async function refresh(){let d=await(await fetch('/api/dashboard')).json();total.textContent=d.reduce((a,x)=>a+x.requested_units,0).toLocaleString()+' uds';rows.innerHTML=d.map(x=>`<tr><td>${x.product_id} · ${x.name}</td><td>${x.category}</td><td>${x.stock}</td><td>${x.attempts}</td><td>${x.requested_units}</td><td>${x.balance}</td><td class="${x.status==='SOBREVENTA'?'bad':x.status==='CRÍTICO'?'warn':'ok'}">${x.status}</td><td class="hide">$${x.revenue_exposure.toFixed(2)}</td></tr>`).join('')}
init()</script></body></html>'''

if __name__ == "__main__":
    if os.getenv("APP_MODE", "web") == "worker":
        from .worker import run; run()
    else:
        import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)
