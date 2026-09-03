from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import Base, engine, db
from .seed import seed
from .analytics import dashboard, anomalies, forecast, restaurant_economics, menu_economics, review_intelligence
from .integrations.swiggy import SwiggyMCP

app = FastAPI(title="FoodPulse API", version="2.0.0", description="Food delivery economics intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(engine)
with next(db()) as s:
    seed(s)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "foodpulse-api", "version": "2.0.0"}

@app.get("/api/dashboard")
def dash(s: Session = Depends(db)): return dashboard(s)

@app.get("/api/anomalies")
def anom(s: Session = Depends(db)): return anomalies(s)

@app.get("/api/forecast")
def fc(s: Session = Depends(db)): return forecast(s)

@app.get("/api/restaurants")
def restaurants(s: Session = Depends(db)):
    rows = s.execute(text("""
        select r.id, r.name, r.area, r.cuisine, r.rating, r.reviews, r.cost_for_two,
               count(o.id) orders,
               coalesce(sum(o.subtotal + o.tax + o.delivery_fee - o.discount),0) gmv,
               coalesce(avg(o.subtotal + o.tax + o.delivery_fee - o.discount),0) aov,
               coalesce(sum(o.platform_fee + o.delivery_fee - o.delivery_cost - o.payment_cost),0) contribution
        from restaurants r left join orders o on o.restaurant_id=r.id
        group by r.id order by contribution desc
    """)).mappings().all()
    return [dict(x) for x in rows]

@app.get("/api/restaurants/{rid}/economics")
def economics(rid: int, s: Session = Depends(db)):
    result = restaurant_economics(s, rid)
    if result is None: raise HTTPException(404, "Restaurant not found")
    return result

@app.get("/api/restaurants/{rid}/menu")
def menu(rid: int, s: Session = Depends(db)):
    return menu_economics(s, rid)

@app.get("/api/reviews/intelligence")
def reviews(s: Session = Depends(db)): return review_intelligence(s)

@app.post("/api/simulator")
def simulator(x: dict):
    subtotal=float(x.get("subtotal",500)); discount=float(x.get("discount",50)); commission=float(x.get("commission_pct",20))/100
    delivery_fee=float(x.get("delivery_fee",30)); delivery_cost=float(x.get("delivery_cost",35)); payment=float(x.get("payment_cost",8))
    platform_revenue=subtotal*commission
    contribution=platform_revenue+delivery_fee-delivery_cost-payment
    margin=(contribution/subtotal*100) if subtotal else 0
    return {"customer_paid":subtotal-discount+delivery_fee,"platform_revenue":platform_revenue,"contribution":contribution,"margin_pct":margin,"annual_contribution":contribution*float(x.get("orders_per_day",100))*365}

@app.get("/api/integrations/swiggy/status")
def swiggy_status():
    sw = SwiggyMCP()
    return {"configured": bool(sw.token), "endpoint": sw.url, "mode": "authorized" if sw.token else "not connected", "auth": "OAuth 2.1 + PKCE"}
