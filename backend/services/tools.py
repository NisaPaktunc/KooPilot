"""
Koopilot Tool Definitions & Handlers
──────────────────────────────────────
Gemini'nin function calling ile çağıracağı tool'lar.
Her tool:
  1. TOOL_DEFINITIONS içinde Gemini schema'sı
  2. Bir Python handler fonksiyonu
"""

import json
from datetime import datetime, timedelta
from database import SessionLocal
from models import Product, Order, Notification


# ── Tool Schema Tanımları (Gemini Function Calling) ───────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "check_stock",
        "description": (
            "Ürün stok durumunu kontrol eder. "
            "Stok kritik eşiğin altındaysa otomatik uyarı bildirim üretir. "
            "Müşteri veya yönetici stok/ürün sorusu sorduğunda çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Ürün adı veya parçası (örn: 'domates', 'zeytinyağı')"
                },
                "product_id": {
                    "type": "string",
                    "description": "Ürün kodu (örn: PRD-001). Biliniyorsa kullan."
                }
            }
        }
    },
    {
        "name": "get_order_status",
        "description": (
            "Sipariş durumunu sorgular. "
            "Sipariş numarası (ORD-xxx) veya müşteri adıyla arama yapılabilir. "
            "Müşteri 'siparişim nerede', 'paketim', 'ORD-xxx' dediğinde çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Sipariş numarası (örn: ORD-128)"
                },
                "customer_name": {
                    "type": "string",
                    "description": "Müşteri adı ile arama"
                }
            }
        }
    },
    {
        "name": "get_cargo_status",
        "description": (
            "Kargo takip numarasıyla teslimat durumunu sorgular. "
            "Sipariş kargodaysa ve tracking numarası varsa çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tracking_number": {
                    "type": "string",
                    "description": "Kargo takip numarası (örn: TRK-4891)"
                },
                "order_id": {
                    "type": "string",
                    "description": "Sipariş ID'si üzerinden tracking numarası bul"
                }
            }
        }
    },
    {
        "name": "send_manager_notification",
        "description": (
            "Yöneticiye kritik durum bildirimi gönderir. "
            "Stok uyarısı, kargo gecikmesi veya acil durumda çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Bildirim başlığı"
                },
                "message": {
                    "type": "string",
                    "description": "Bildirim detay mesajı"
                },
                "priority": {
                    "type": "string",
                    "enum": ["dusuk", "orta", "yuksek", "kritik"],
                    "description": "Bildirim önceliği"
                },
                "type": {
                    "type": "string",
                    "description": "Bildirim tipi: stok_uyari, kargo_gecikme, genel"
                }
            },
            "required": ["title", "message"]
        }
    },
    {
        "name": "get_daily_summary",
        "description": (
            "Günlük operasyon özetini getirir: sipariş sayıları, kritik stoklar. "
            "Yönetici 'bugün ne var', 'özet', 'durum nedir' dediğinde çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Tarih YYYY-MM-DD formatında. Boş bırakılırsa bugün."
                }
            }
        }
    }
]


# ── Tool Handler Fonksiyonları ────────────────────────────────────────────────

def _load_cargo_mock() -> dict:
    try:
        with open("mock_data/cargo_responses.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def check_stock(product_name: str = None, product_id: str = None) -> str:
    db = SessionLocal()
    try:
        query = db.query(Product)
        if product_id:
            product = query.filter(Product.id == product_id).first()
        elif product_name:
            product = query.filter(Product.name.ilike(f"%{product_name}%")).first()
        else:
            return "Ürün adı veya kodu belirtilmedi."

        if not product:
            return f"'{product_name or product_id}' adlı ürün veritabanında bulunamadı."

        durum = "mevcut ✅" if product.stock_quantity > product.low_threshold else (
            "KRİTİK SEVIYE ⚠️" if product.stock_quantity > 0 else "TÜKENDİ 🔴"
        )

        # Kritik stoksa otomatik bildirim üret
        if product.stock_quantity <= product.low_threshold:
            _save_notification(
                title=f"⚠️ Kritik Stok: {product.name}",
                message=(
                    f"{product.name} stoğu kritik seviyede! "
                    f"Mevcut: {product.stock_quantity} {product.unit} "
                    f"(Eşik: {product.low_threshold})"
                ),
                priority="yuksek",
                notif_type="stok_uyari",
                db=db
            )

        return (
            f"Ürün: {product.name} | "
            f"Kod: {product.id} | "
            f"Stok: {product.stock_quantity} {product.unit} | "
            f"Durum: {durum} | "
            f"Fiyat: {product.unit_price} TL"
        )
    finally:
        db.close()


def get_order_status(order_id: str = None, customer_name: str = None) -> str:
    db = SessionLocal()
    try:
        query = db.query(Order)
        if order_id:
            order = query.filter(Order.id == order_id).first()
        elif customer_name:
            order = query.filter(
                Order.customer_name.ilike(f"%{customer_name}%")
            ).first()
        else:
            return "Sipariş numarası veya müşteri adı belirtilmedi."

        if not order:
            return f"Sipariş bulunamadı. (Aranan: {order_id or customer_name})"

        status_map = {
            "beklemede":      "Beklemede 🕐",
            "hazirlaniyor":   "Hazırlanıyor 📦",
            "kargoda":        "Kargoya Verildi 🚚",
            "teslim_edildi":  "Teslim Edildi ✅",
            "iptal":          "İptal Edildi ❌",
        }
        durum = status_map.get(order.status, order.status)

        result = (
            f"Sipariş No: {order.id} | "
            f"Müşteri: {order.customer_name} | "
            f"Durum: {durum} | "
            f"Tutar: {order.total_amount} TL"
        )

        if order.tracking_number:
            result += f" | Kargo Takip: {order.tracking_number} ({order.cargo_company or 'Kargo'})"

        return result
    finally:
        db.close()


def get_cargo_status(tracking_number: str = None, order_id: str = None) -> str:
    db = SessionLocal()
    try:
        # order_id ile tracking bul
        if order_id and not tracking_number:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order and order.tracking_number:
                tracking_number = order.tracking_number
            else:
                return "Bu siparişe ait kargo takip numarası henüz tanımlanmamış."

        if not tracking_number:
            return "Kargo takip numarası bulunamadı."

        cargo_data = _load_cargo_mock()
        info = cargo_data.get(tracking_number)

        if not info:
            # Bilinmeyen tracking — genel yanıt
            return (
                f"Takip No: {tracking_number} | "
                "Durum: Dağıtımda 🚚 | Tahmini teslim: Bugün 14:00-18:00"
            )

        # Gecikme varsa yönetici bildirimi
        if info.get("gecikme"):
            _save_notification(
                title=f"🚨 Kargo Gecikmesi: {tracking_number}",
                message=(
                    f"Kargo gecikmesi tespit edildi. "
                    f"Neden: {info.get('gecikme_nedeni', 'Belirtilmedi')}. "
                    f"Yeni tahmini teslim: {info.get('tahmini_teslim', '?')}"
                ),
                priority="yuksek",
                notif_type="kargo_gecikme",
                db=db
            )

        return (
            f"Takip No: {tracking_number} | "
            f"Durum: {info['durum']} | "
            f"Konum: {info['konum']} | "
            f"Tahmini Teslim: {info['tahmini_teslim']} | "
            f"Son Güncelleme: {info.get('son_guncelleme', '-')}"
            + (f" | ⚠️ GECİKME: {info.get('gecikme_nedeni', '')}" if info.get("gecikme") else "")
        )
    finally:
        db.close()


def send_manager_notification(
    title: str,
    message: str,
    priority: str = "orta",
    type: str = "genel"
) -> str:
    db = SessionLocal()
    try:
        notif_id = _save_notification(
            title=title,
            message=message,
            priority=priority,
            notif_type=type,
            db=db
        )
        return f"✅ Bildirim gönderildi (ID: {notif_id}) | Başlık: {title} | Öncelik: {priority}"
    finally:
        db.close()


def get_daily_summary(date: str = None) -> str:
    from datetime import date as date_cls
    db = SessionLocal()
    try:
        total_orders  = db.query(Order).count()
        pending       = db.query(Order).filter(Order.status == "beklemede").count()
        preparing     = db.query(Order).filter(Order.status == "hazirlaniyor").count()
        in_cargo      = db.query(Order).filter(Order.status == "kargoda").count()
        delivered     = db.query(Order).filter(Order.status == "teslim_edildi").count()
        critical_stock = db.query(Product).filter(
            Product.stock_quantity <= Product.low_threshold
        ).count()
        out_of_stock = db.query(Product).filter(Product.stock_quantity == 0).count()

        return (
            f"📊 Günlük Özet ({date or str(date_cls.today())}) | "
            f"Toplam Sipariş: {total_orders} | "
            f"Beklemede: {pending} | "
            f"Hazırlanıyor: {preparing} | "
            f"Kargoda: {in_cargo} | "
            f"Teslim Edildi: {delivered} | "
            f"Kritik Stok: {critical_stock} ürün | "
            f"Tükenen: {out_of_stock} ürün"
        )
    finally:
        db.close()


# ── Yardımcı: DB'ye bildirim kaydet (24 saat deduplikasyonlu) ─────────────────

def _save_notification(title, message, priority, notif_type, db) -> int:
    """Aynı başlıkta son 24 saat içinde bildirim varsa tekrar oluşturmaz."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    existing = (
        db.query(Notification)
        .filter(
            Notification.title == title,
            Notification.created_at >= cutoff,
        )
        .first()
    )
    if existing:
        return existing.id

    notif = Notification(
        type=notif_type,
        title=title,
        message=message,
        priority=priority
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif.id


# ── Tool Dispatcher ───────────────────────────────────────────────────────────

TOOL_HANDLERS = {
    "check_stock":               check_stock,
    "get_order_status":          get_order_status,
    "get_cargo_status":          get_cargo_status,
    "send_manager_notification": send_manager_notification,
    "get_daily_summary":         get_daily_summary,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return f"Bilinmeyen araç: {tool_name}"
    try:
        return handler(**tool_input)
    except Exception as e:
        return f"Tool hatası ({tool_name}): {str(e)}"
