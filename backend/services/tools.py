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
from models import Product, Order, OrderItem, Notification


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
    },
    {
        "name": "list_all_products",
        "description": (
            "Tüm ürünleri veya belirli kategorideki ürünleri listeler. "
            "Kullanıcı 'hangi ürünler var', 'sebzeler', 'kategoriler' dediğinde çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filtrelemek için kategori (örn: 'sebze', 'baharat', 'organik'). Boş bırakılırsa tümünü listeler."
                }
            }
        }
    },
    {
        "name": "get_sales_analytics",
        "description": (
            "Satış analitiklerini getirir: en çok satan ürünler, kategori bazlı gelir, "
            "sipariş durum dağılımı, ortalama sipariş tutarı. "
            "Yönetici 'satış analizi', 'en çok satan', 'gelir', 'performans' dediğinde çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "enum": ["top_products", "category_revenue", "order_status", "full_report"],
                    "description": "İstenen metrik. Varsayılan: full_report"
                }
            }
        }
    },
    {
        "name": "get_stock_forecast",
        "description": (
            "Stok tükenme tahmini yapar. Mevcut stok ve sipariş verileriyle "
            "hangi ürünlerin ne zaman tükeneceğini tahmin eder. "
            "Yönetici 'stok tahmini', 'ne zaman biter', 'hangi ürünler tükenecek' dediğinde çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filtrelemek için kategori. Boş bırakılırsa tüm kritik ürünleri gösterir."
                }
            }
        }
    },
    {
        "name": "draft_supplier_order",
        "description": (
            "Kritik stok durumunda tedarikçiye sipariş e-posta taslağı oluşturur. "
            "Stok kritik seviyeye düştüğünde ve yönetici tedarikçiye haber vermek istediğinde çağır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Sipariş verilecek ürünün kodu (örn: PRD-001)"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Sipariş verilecek miktar"
                },
                "note": {
                    "type": "string",
                    "description": "Tedarikçiye özel not (opsiyonel)"
                }
            },
            "required": ["product_id", "quantity"]
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
            # Eğer bulunamadıysa ve başında ORD- yoksa ekleyip tekrar dene
            if not order and not order_id.startswith("ORD-"):
                order = query.filter(Order.id == f"ORD-{order_id}").first()
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


def list_all_products(category: str = None) -> str:
    db = SessionLocal()
    try:
        query = db.query(Product)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        products = query.order_by(Product.category, Product.name).all()

        if not products:
            return f"'{category}' kategorisinde ürün bulunamadı."

        # Kategori bazlı grupla
        categories = {}
        for p in products:
            cat = p.category or "genel"
            if cat not in categories:
                categories[cat] = []
            durum = "✅" if p.stock_quantity > p.low_threshold else (
                "⚠️ KRİTİK" if p.stock_quantity > 0 else "🔴 TÜKENDİ"
            )
            categories[cat].append(
                f"  • {p.name} ({p.id}): {p.stock_quantity} {p.unit} — {p.unit_price} TL [{durum}]"
            )

        lines = [f"📦 Toplam {len(products)} ürün:"]
        for cat, items in categories.items():
            lines.append(f"\n**{cat.upper()}** ({len(items)} ürün):")
            lines.extend(items)

        return "\n".join(lines)
    finally:
        db.close()


def get_sales_analytics(metric: str = "full_report") -> str:
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        items = db.query(OrderItem).all()

        total_orders = len(orders)
        total_revenue = sum(o.total_amount or 0 for o in orders)
        avg_order = total_revenue / total_orders if total_orders > 0 else 0

        # Sipariş durum dağılımı
        status_counts = {}
        for o in orders:
            status_counts[o.status] = status_counts.get(o.status, 0) + 1

        status_labels = {
            "beklemede": "Beklemede", "hazirlaniyor": "Hazırlanıyor",
            "kargoda": "Kargoda", "teslim_edildi": "Teslim Edildi", "iptal": "İptal"
        }

        # En çok satılan ürünler (miktar bazlı)
        product_sales = {}
        product_revenue = {}
        for item in items:
            pid = item.product_id
            product_sales[pid] = product_sales.get(pid, 0) + item.quantity
            product_revenue[pid] = product_revenue.get(pid, 0) + (item.quantity * item.unit_price)

        top_by_qty = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        top_by_rev = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

        # Ürün adlarını çek
        product_names = {}
        for pid in set(list(product_sales.keys()) + list(product_revenue.keys())):
            prod = db.query(Product).filter(Product.id == pid).first()
            if prod:
                product_names[pid] = prod.name

        # Kategori bazlı gelir
        category_rev = {}
        for item in items:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            if prod:
                cat = prod.category or "genel"
                category_rev[cat] = category_rev.get(cat, 0) + (item.quantity * item.unit_price)

        lines = ["📊 **SATIŞ ANALİTİKLERİ**", ""]

        if metric in ("full_report", "order_status"):
            lines.append("**Sipariş Özeti:**")
            lines.append(f"  • Toplam Sipariş: {total_orders}")
            lines.append(f"  • Toplam Ciro: {total_revenue:,.0f} TL")
            lines.append(f"  • Ortalama Sipariş: {avg_order:,.0f} TL")
            lines.append("")
            lines.append("**Durum Dağılımı:**")
            for status, count in status_counts.items():
                label = status_labels.get(status, status)
                pct = (count / total_orders * 100) if total_orders > 0 else 0
                lines.append(f"  • {label}: {count} (%{pct:.0f})")

        if metric in ("full_report", "top_products"):
            lines.append("")
            lines.append("**En Çok Satan 5 Ürün (Miktar):**")
            for i, (pid, qty) in enumerate(top_by_qty, 1):
                name = product_names.get(pid, pid)
                lines.append(f"  {i}. {name}: {qty} adet")

            lines.append("")
            lines.append("**En Çok Gelir Getiren 5 Ürün:**")
            for i, (pid, rev) in enumerate(top_by_rev, 1):
                name = product_names.get(pid, pid)
                lines.append(f"  {i}. {name}: {rev:,.0f} TL")

        if metric in ("full_report", "category_revenue"):
            lines.append("")
            lines.append("**Kategori Bazlı Gelir:**")
            sorted_cats = sorted(category_rev.items(), key=lambda x: x[1], reverse=True)
            for cat, rev in sorted_cats:
                pct = (rev / total_revenue * 100) if total_revenue > 0 else 0
                lines.append(f"  • {cat}: {rev:,.0f} TL (%{pct:.0f})")

        return "\n".join(lines)
    finally:
        db.close()


def get_stock_forecast(category: str = None) -> str:
    db = SessionLocal()
    try:
        query = db.query(Product)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        products = query.all()

        forecasts = []
        for p in products:
            # Sipariş kalemleri üzerinden ortalama günlük tüketim tahmin et
            items = db.query(OrderItem).filter(OrderItem.product_id == p.id).all()
            total_sold = sum(i.quantity for i in items)

            # Mock: ortalama 7 günlük veri varsay
            daily_consumption = total_sold / 7 if total_sold > 0 else 0
            days_left = int(p.stock_quantity / daily_consumption) if daily_consumption > 0 else -1

            if p.stock_quantity == 0:
                forecasts.append({
                    "name": p.name, "id": p.id, "category": p.category,
                    "stock": p.stock_quantity, "unit": p.unit,
                    "daily_use": daily_consumption, "days_left": 0,
                    "risk": "TÜKENDİ"
                })
            elif days_left >= 0 and days_left <= 7:
                forecasts.append({
                    "name": p.name, "id": p.id, "category": p.category,
                    "stock": p.stock_quantity, "unit": p.unit,
                    "daily_use": daily_consumption, "days_left": days_left,
                    "risk": "KRİTİK" if days_left <= 3 else "DİKKAT"
                })
            elif p.stock_quantity <= p.low_threshold:
                forecasts.append({
                    "name": p.name, "id": p.id, "category": p.category,
                    "stock": p.stock_quantity, "unit": p.unit,
                    "daily_use": daily_consumption, "days_left": days_left,
                    "risk": "DÜŞÜK"
                })

        if not forecasts:
            return "Tüm ürünlerin stok seviyesi güvenli aralıkta. Kritik ürün yok."

        # Risk seviyesine göre sırala
        risk_order = {"TÜKENDİ": 0, "KRİTİK": 1, "DİKKAT": 2, "DÜŞÜK": 3}
        forecasts.sort(key=lambda x: risk_order.get(x["risk"], 99))

        lines = [f"📈 **STOK TAHMİNİ** — {len(forecasts)} ürün risk altında:", ""]
        risk_icons = {"TÜKENDİ": "🔴", "KRİTİK": "🟠", "DİKKAT": "🟡", "DÜŞÜK": "🟢"}

        for f in forecasts:
            icon = risk_icons.get(f["risk"], "⚪")
            days_text = f"{f['days_left']} gün" if f["days_left"] > 0 else "ŞİMDİ"
            daily_text = f" (günlük ~{f['daily_use']:.1f} {f['unit']})" if f["daily_use"] > 0 else ""
            lines.append(
                f"{icon} **{f['name']}** [{f['risk']}]: "
                f"{f['stock']} {f['unit']} kaldı → tahmini tükenme: {days_text}{daily_text}"
            )

        lines.append("")
        critical = sum(1 for f in forecasts if f["risk"] in ("TÜKENDİ", "KRİTİK"))
        if critical > 0:
            lines.append(f"⚠️ {critical} ürün için ACİL tedarik önerisi: Tedarikçi ile iletişime geçilmeli.")

        return "\n".join(lines)
    finally:
        db.close()


def draft_supplier_order(product_id: str, quantity: int, note: str = None) -> str:
    from models import Supplier
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return f"❌ Hata: {product_id} kodlu ürün bulunamadı."
        
        supplier = db.query(Supplier).filter(Supplier.id == product.supplier_id).first()
        supplier_name = supplier.name if supplier else "Bilinmeyen Tedarikçi"
        supplier_email = supplier.email if supplier else "tedarik@sirket.com"

        # E-posta taslağı oluştur
        subject = f"Tedarik Talebi: {product.name} ({product_id})"
        body = (
            f"Sayın {supplier_name},\n\n"
            f"Aşağıdaki ürün için stoklarımız kritik seviyeye düşmüştür. "
            f"Acil olarak tedarik edilmesini rica ederiz:\n\n"
            f"- Ürün: {product.name}\n"
            f"- Ürün Kodu: {product_id}\n"
            f"- Talep Edilen Miktar: {quantity} {product.unit}\n"
        )
        if note:
            body += f"- Not: {note}\n"
        
        body += "\nİyi çalışmalar dileriz.\nKoopilot Otomatik Tedarik Sistemi"

        # Bildirim olarak kaydet
        _save_notification(
            title=f"📧 Taslak Hazır: {product.name}",
            message=f"{supplier_name} için {quantity} {product.unit} sipariş taslağı oluşturuldu.",
            priority="orta",
            notif_type="tedarik_talebi",
            db=db
        )

        return (
            f"✅ {supplier_name} için e-posta taslağı hazırlandı:\n\n"
            f"**Konu:** {subject}\n"
            f"**Alıcı:** {supplier_email}\n\n"
            f"**Mesaj:**\n{body}"
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
    "list_all_products":         list_all_products,
    "get_sales_analytics":       get_sales_analytics,
    "get_stock_forecast":        get_stock_forecast,
    "draft_supplier_order":      draft_supplier_order,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return f"Bilinmeyen araç: {tool_name}"
    try:
        return handler(**tool_input)
    except Exception as e:
        return f"Tool hatası ({tool_name}): {str(e)}"
