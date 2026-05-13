from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import engine, SessionLocal
from models import Base, Product, Order, OrderItem, Notification, Message, Supplier
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


# ── Tam CRUD Pydantic Modelleri ───────────────────────────────────────────────

class ProductCreate(BaseModel):
    id: Optional[str] = None
    name: str
    category: str = "genel"
    stock_quantity: int = 0
    low_threshold: int = 10
    unit_price: float = 0.0
    unit: str = "adet"
    supplier_id: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    low_threshold: Optional[int] = None
    unit_price: Optional[float] = None
    unit: Optional[str] = None
    supplier_id: Optional[str] = None

class OrderCreate(BaseModel):
    id: Optional[str] = None
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    status: str = "beklemede"
    total_amount: float = 0.0
    tracking_number: Optional[str] = None
    cargo_company: Optional[str] = None
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None
    tracking_number: Optional[str] = None
    cargo_company: Optional[str] = None
    notes: Optional[str] = None

class SupplierCreate(BaseModel):
    id: Optional[str] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


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
        print(f"AI hatasi: {e}")
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


# ── WhatsApp Webhook ──────────────────────────────────────────────────────────

from fastapi import Form, BackgroundTasks, Response
from integrations.whatsapp import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)

async def process_whatsapp_message(sender_id: str, message_text: str):
    """
    Background task to process WhatsApp message, call AI, and send response back.
    sender_id is used as session_id.
    """
    db = SessionLocal()
    try:
        # Konuşma geçmişini çek (son 10 mesaj)
        history_rows = (
            db.query(Message)
            .filter(Message.session_id == sender_id)
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
        db.add(Message(session_id=sender_id, role="user", content=message_text))
        db.commit()

    finally:
        db.close()

    # Agent çağır
    try:
        result = get_ai_response(message_text, gemini_history)
        response_text = result["response"]
    except Exception as e:
        logger.error(f"WhatsApp AI hatası: {e}")
        response_text = "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."

    # Yanıtı kaydet ve WhatsApp üzerinden gönder
    db = SessionLocal()
    try:
        db.add(Message(session_id=sender_id, role="assistant", content=response_text))
        db.commit()

        # Bildirim varsa WebSocket ile yayınla
        latest_notif = db.query(Notification).order_by(Notification.id.desc()).first()
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

    # WhatsApp mesajını gönder
    send_whatsapp_message(sender_id, response_text)


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(background_tasks: BackgroundTasks, Body: str = Form(...), From: str = Form(...)):
    """
    Twilio WhatsApp Sandbox Webhook
    """
    logger.info(f"Received WhatsApp message from {From}: {Body}")
    
    # AI işlemini arka planda başlat (Twilio timeout olmaması için hemen 200 OK döneriz)
    background_tasks.add_task(process_whatsapp_message, From, Body)
    
    # Twilio'nun hata vermemesi için boş bir TwiML response dönüyoruz
    # Gerçek yanıt background task içinden REST API ile gidecek
    return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>', media_type="application/xml")


@app.get("/whatsapp/status")
def whatsapp_status():
    import os
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    phone = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    is_connected = bool(sid and token and phone)
    
    return {
        "is_connected": is_connected,
        "phone": phone,
        "webhook_url": "POST /webhook/whatsapp"
    }


@app.get("/whatsapp/sessions")
def get_whatsapp_sessions():
    db = SessionLocal()
    try:
        from sqlalchemy import func
        # Find all unique session_ids that start with whatsapp:
        sessions = db.query(
            Message.session_id, 
            func.max(Message.timestamp).label("last_message")
        ).filter(Message.session_id.like("whatsapp:%")).group_by(Message.session_id).order_by(func.max(Message.timestamp).desc()).all()
        
        return [
            {
                "session_id": s.session_id,
                "phone": s.session_id.replace("whatsapp:", ""),
                "last_message": s.last_message.isoformat() if s.last_message else None
            } for s in sessions
        ]
    finally:
        db.close()


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


@app.post("/products")
def create_product(body: ProductCreate):
    db = SessionLocal()
    try:
        pid = body.id or f"PRD-{db.query(Product).count() + 1:03d}"
        existing = db.query(Product).filter(Product.id == pid).first()
        if existing:
            return {"error": f"{pid} kodlu ürün zaten mevcut"}
        product = Product(
            id=pid, name=body.name, category=body.category,
            stock_quantity=body.stock_quantity, low_threshold=body.low_threshold,
            unit_price=body.unit_price, unit=body.unit, supplier_id=body.supplier_id
        )
        db.add(product)
        db.commit()
        return {"success": True, "id": pid, "name": body.name}
    finally:
        db.close()


@app.put("/products/{product_id}")
def update_product(product_id: str, body: ProductUpdate):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "Ürün bulunamadı"}
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(product, field, value)
        db.commit()
        return {"success": True, "id": product_id}
    finally:
        db.close()


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "Ürün bulunamadı"}
        db.query(OrderItem).filter(OrderItem.product_id == product_id).delete()
        db.delete(product)
        db.commit()
        return {"success": True, "id": product_id}
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


@app.post("/orders")
def create_order(body: OrderCreate):
    db = SessionLocal()
    try:
        oid = body.id or f"ORD-{db.query(Order).count() + 1:03d}"
        existing = db.query(Order).filter(Order.id == oid).first()
        if existing:
            return {"error": f"{oid} numaralı sipariş zaten mevcut"}
        order = Order(
            id=oid, customer_name=body.customer_name, customer_phone=body.customer_phone,
            customer_email=body.customer_email, status=body.status,
            total_amount=body.total_amount, tracking_number=body.tracking_number,
            cargo_company=body.cargo_company, notes=body.notes
        )
        db.add(order)
        db.commit()
        return {"success": True, "id": oid, "customer": body.customer_name}
    finally:
        db.close()


@app.put("/orders/{order_id}")
def update_order(order_id: str, body: OrderUpdate):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"error": "Sipariş bulunamadı"}
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(order, field, value)
        db.commit()
        return {"success": True, "id": order_id}
    finally:
        db.close()


@app.delete("/orders/{order_id}")
def delete_order(order_id: str):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"error": "Sipariş bulunamadı"}
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        db.delete(order)
        db.commit()
        return {"success": True, "id": order_id}
    finally:
        db.close()


# ── Tedarikçiler ──────────────────────────────────────────────────────────────────

@app.get("/suppliers")
def get_suppliers():
    db = SessionLocal()
    try:
        suppliers = db.query(Supplier).all()
        return [
            {"id": s.id, "name": s.name, "email": s.email, "phone": s.phone,
             "product_count": db.query(Product).filter(Product.supplier_id == s.id).count()}
            for s in suppliers
        ]
    finally:
        db.close()


@app.post("/suppliers")
def create_supplier(body: SupplierCreate):
    db = SessionLocal()
    try:
        sid = body.id or f"SUP-{db.query(Supplier).count() + 1:03d}"
        existing = db.query(Supplier).filter(Supplier.id == sid).first()
        if existing:
            return {"error": f"{sid} kodlu tedarikçi zaten mevcut"}
        supplier = Supplier(id=sid, name=body.name, email=body.email, phone=body.phone)
        db.add(supplier)
        db.commit()
        return {"success": True, "id": sid, "name": body.name}
    finally:
        db.close()


@app.put("/suppliers/{supplier_id}")
def update_supplier(supplier_id: str, body: SupplierUpdate):
    db = SessionLocal()
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return {"error": "Tedarikçi bulunamadı"}
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(supplier, field, value)
        db.commit()
        return {"success": True, "id": supplier_id}
    finally:
        db.close()


@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: str):
    db = SessionLocal()
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return {"error": "Tedarikçi bulunamadı"}
        db.delete(supplier)
        db.commit()
        return {"success": True, "id": supplier_id}
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


# ── Dashboard Akıllı İçgörüler ────────────────────────────────────────────────

@app.get("/dashboard/insights")
def dashboard_insights():
    from services.analytics_engine import generate_insights
    return generate_insights()


# ── Dosya Yuklemesi (Excel / CSV Import) ──────────────────────────────────────

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), data_type: str = None):
    """Excel veya CSV dosyasi yukleyerek toplu veri aktarimi."""
    from services.import_service import import_file
    content = await file.read()
    result = import_file(content, file.filename, data_type)
    return result


@app.post("/upload/preview")
async def upload_preview(file: UploadFile = File(...)):
    """Dosyanin ilk 5 satirini onizler, veri tipini otomatik tespit eder."""
    from services.import_service import preview_file
    content = await file.read()
    return preview_file(content, file.filename)


# ── WebSocket: Canli Bildirimler ──────────────────────────────────────────────

@app.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(30)  # bağlantıyı canlı tut
    except WebSocketDisconnect:
        manager.disconnect(websocket)
