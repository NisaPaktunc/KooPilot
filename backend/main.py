from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import engine, SessionLocal
from models import Base, Product, Order, OrderItem, Notification, Message
from services.ai_service import get_ai_response
import uuid
import json
import asyncio

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Koopilot API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── WebSocket Bağlantı Yöneticisi (canlı bildirimler için) ────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(data, ensure_ascii=False))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)


manager = ConnectionManager()


# ── Pydantic Modeller ─────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str


class StockUpdate(BaseModel):
    quantity: int


# ── Temel ─────────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Koopilot API v2 çalışıyor ⚡"}


# ── Chat Endpoint'i ───────────────────────────────────────────────────────────

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    session_id   = request.session_id or str(uuid.uuid4())
    db           = SessionLocal()

    try:
        # Konuşma geçmişini çek (son 10 mesaj)
        history_rows = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.timestamp.desc())
            .limit(10)
            .all()
        )
        history_rows.reverse()

        # Gemini formatına çevir
        from google.genai import types as gtypes
        gemini_history = []
        for row in history_rows:
            gemini_history.append(
                gtypes.Content(
                    role="user" if row.role == "user" else "model",
                    parts=[gtypes.Part(text=row.content)]
                )
            )

        # Kullanıcı mesajını kaydet
        db.add(Message(session_id=session_id, role="user", content=user_message))
        db.commit()

    finally:
        db.close()

    # Agent çağır
    try:
        result        = get_ai_response(user_message, gemini_history)
        response_text = result["response"]
        tools_used    = result["tools_used"]
        tool_details  = result["tool_details"]
    except Exception as e:
        print(f"❌ AI hatası: {e}")
        response_text = f"Üzgünüm, bir hata oluştu. ({str(e)[:100]})"
        tools_used    = []
        tool_details  = []

    # Yanıtı kaydet
    db = SessionLocal()
    try:
        db.add(Message(session_id=session_id, role="assistant", content=response_text))
        db.commit()

        # Eğer yeni bildirim oluştuysa WebSocket ile yayınla
        latest_notif = (
            db.query(Notification)
            .order_by(Notification.id.desc())
            .first()
        )
        if latest_notif and not latest_notif.is_read:
            await manager.broadcast({
                "type":     "new_notification",
                "id":       latest_notif.id,
                "title":    latest_notif.title,
                "message":  latest_notif.message,
                "priority": latest_notif.priority,
                "notif_type": latest_notif.type,
            })
    finally:
        db.close()

    return {
        "response":     response_text,
        "session_id":   session_id,
        "tools_used":   tools_used,
        "tool_details": tool_details,
    }


# ── Konuşma Geçmişi ───────────────────────────────────────────────────────────

@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    db = SessionLocal()
    try:
        msgs = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.timestamp)
            .all()
        )
        return [
            {
                "role":      m.role,
                "content":   m.content,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            }
            for m in msgs
        ]
    finally:
        db.close()


# ── Ürünler ───────────────────────────────────────────────────────────────────

@app.get("/products")
def get_products():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return [
            {
                "id":             p.id,
                "name":           p.name,
                "category":       p.category,
                "stock_quantity": p.stock_quantity,
                "low_threshold":  p.low_threshold,
                "unit_price":     p.unit_price,
                "unit":           p.unit,
                "is_critical":    p.stock_quantity <= p.low_threshold,
            }
            for p in products
        ]
    finally:
        db.close()


@app.get("/products/low-stock")
def get_low_stock():
    db = SessionLocal()
    try:
        products = db.query(Product).filter(
            Product.stock_quantity <= Product.low_threshold
        ).all()
        return [
            {
                "id":             p.id,
                "name":           p.name,
                "stock_quantity": p.stock_quantity,
                "low_threshold":  p.low_threshold,
                "unit":           p.unit,
                "is_out":         p.stock_quantity == 0,
            }
            for p in products
        ]
    finally:
        db.close()


@app.patch("/products/{product_id}/stock")
async def update_stock(product_id: str, body: StockUpdate):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "Ürün bulunamadı"}
        product.stock_quantity = body.quantity
        db.commit()
        return {"success": True, "product_id": product_id, "new_quantity": body.quantity}
    finally:
        db.close()


# ── Siparişler ────────────────────────────────────────────────────────────────

@app.get("/orders")
def get_orders(status: Optional[str] = None, limit: int = 50):
    db = SessionLocal()
    try:
        query = db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        orders = query.order_by(Order.created_at.desc()).limit(limit).all()
        return [
            {
                "id":              o.id,
                "customer_name":   o.customer_name,
                "customer_phone":  o.customer_phone,
                "status":          o.status,
                "total_amount":    o.total_amount,
                "tracking_number": o.tracking_number,
                "cargo_company":   o.cargo_company,
                "created_at":      o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]
    finally:
        db.close()


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"error": "Sipariş bulunamadı"}
        return {
            "id":              order.id,
            "customer_name":   order.customer_name,
            "customer_phone":  order.customer_phone,
            "status":          order.status,
            "total_amount":    order.total_amount,
            "tracking_number": order.tracking_number,
            "cargo_company":   order.cargo_company,
            "notes":           order.notes,
            "created_at":      order.created_at.isoformat() if order.created_at else None,
        }
    finally:
        db.close()


@app.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, body: OrderStatusUpdate):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"error": "Sipariş bulunamadı"}
        order.status = body.status
        db.commit()

        # Bildirim gönder
        notif = Notification(
            type="siparis_guncelleme",
            title=f"Sipariş Güncellendi: {order_id}",
            message=f"{order.customer_name} siparişi '{body.status}' durumuna alındı.",
            priority="dusuk"
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        await manager.broadcast({
            "type":     "new_notification",
            "id":       notif.id,
            "title":    notif.title,
            "message":  notif.message,
            "priority": notif.priority,
        })

        return {"success": True, "order_id": order_id, "new_status": body.status}
    finally:
        db.close()


# ── Bildirimler ───────────────────────────────────────────────────────────────

@app.get("/notifications")
def get_notifications(limit: int = 30):
    db = SessionLocal()
    try:
        notifs = (
            db.query(Notification)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id":         n.id,
                "type":       n.type,
                "title":      n.title,
                "message":    n.message,
                "priority":   n.priority,
                "is_read":    n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ]
    finally:
        db.close()


@app.patch("/notifications/read-all")
def mark_all_read():
    db = SessionLocal()
    try:
        db.query(Notification).filter(Notification.is_read == False).update(
            {"is_read": True}
        )
        db.commit()
        return {"success": True}
    finally:
        db.close()


@app.patch("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int):
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(Notification.id == notif_id).first()
        if notif:
            notif.is_read = True
            db.commit()
        return {"success": True}
    finally:
        db.close()


# ── Dashboard Özet ────────────────────────────────────────────────────────────

@app.get("/dashboard/summary")
def dashboard_summary():
    db = SessionLocal()
    try:
        total_orders    = db.query(Order).count()
        pending         = db.query(Order).filter(Order.status == "beklemede").count()
        in_cargo        = db.query(Order).filter(Order.status == "kargoda").count()
        delivered       = db.query(Order).filter(Order.status == "teslim_edildi").count()
        critical_stock  = db.query(Product).filter(
            Product.stock_quantity <= Product.low_threshold
        ).count()
        unread_notifs   = db.query(Notification).filter(
            Notification.is_read == False
        ).count()

        return {
            "total_orders":   total_orders,
            "pending":        pending,
            "in_cargo":       in_cargo,
            "delivered":      delivered,
            "critical_stock": critical_stock,
            "unread_notifs":  unread_notifs,
        }
    finally:
        db.close()


# ── Dashboard Analitik ────────────────────────────────────────────────────────

@app.get("/dashboard/analytics")
def dashboard_analytics():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        items  = db.query(OrderItem).all()

        total_revenue = sum(o.total_amount or 0 for o in orders)

        # Sipariş durum dağılımı
        status_counts = {}
        for o in orders:
            status_counts[o.status] = status_counts.get(o.status, 0) + 1

        # Ürün bazlı satış
        product_sales = {}
        product_revenue = {}
        for item in items:
            pid = item.product_id
            product_sales[pid] = product_sales.get(pid, 0) + item.quantity
            product_revenue[pid] = product_revenue.get(pid, 0) + (item.quantity * item.unit_price)

        # Ürün adlarını çek
        product_names = {}
        for pid in set(list(product_sales.keys())):
            prod = db.query(Product).filter(Product.id == pid).first()
            if prod:
                product_names[pid] = prod.name

        # Top 5 ürün (miktar)
        top_products = [
            {"name": product_names.get(pid, pid), "quantity": qty}
            for pid, qty in sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Top 5 ürün (gelir)
        top_revenue = [
            {"name": product_names.get(pid, pid), "revenue": rev}
            for pid, rev in sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Kategori bazlı gelir
        category_rev = {}
        for item in items:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            if prod:
                cat = prod.category or "genel"
                category_rev[cat] = category_rev.get(cat, 0) + (item.quantity * item.unit_price)

        category_data = [
            {"category": cat, "revenue": rev}
            for cat, rev in sorted(category_rev.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_revenue":  total_revenue,
            "total_orders":   len(orders),
            "avg_order":      total_revenue / len(orders) if orders else 0,
            "status_counts":  status_counts,
            "top_products":   top_products,
            "top_revenue":    top_revenue,
            "category_data":  category_data,
        }
    finally:
        db.close()


# ── WebSocket: Canlı Bildirimler ──────────────────────────────────────────────

@app.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(30)  # bağlantıyı canlı tut
    except WebSocketDisconnect:
        manager.disconnect(websocket)
