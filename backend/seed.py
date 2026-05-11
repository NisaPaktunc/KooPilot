"""
Koopilot Demo Verisi
─────────────────────
Çalıştır: python seed.py
Demo için gerçekçi veri yükler.
"""

from database import engine, SessionLocal
from models import Base, Product, Order, Supplier, Notification

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def add_if_not_exists(model, id_field="id", **kwargs):
    existing = db.query(model).filter(
        getattr(model, id_field) == kwargs[id_field]
    ).first()
    if not existing:
        obj = model(**kwargs)
        db.add(obj)
        return True
    return False


print("🌱 Seed verisi yükleniyor...\n")

# ── Tedarikçiler ──────────────────────────────────────────────────────────────
suppliers = [
    dict(id="SUP-001", name="Anadolu Gıda AŞ",   email="siparis@anadolugida.com",  phone="0212 555 0001"),
    dict(id="SUP-002", name="Marmara Sebze Ltd",  email="info@marmarasebze.com",    phone="0216 555 0002"),
    dict(id="SUP-003", name="Ege Organik Tarım",  email="uretim@egeorganik.com",    phone="0232 555 0003"),
]
for s in suppliers:
    if add_if_not_exists(Supplier, **s):
        print(f"  ✅ Tedarikçi: {s['name']}")

# ── Ürünler ───────────────────────────────────────────────────────────────────
# Bazıları kasıtlı olarak kritik stokta — demo için!
products = [
    dict(id="PRD-001", name="Domates",       category="sebze",  stock_quantity=48,  low_threshold=50,  unit_price=25.0,  unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-002", name="Zeytinyağı",    category="yağ",    stock_quantity=120, low_threshold=20,  unit_price=180.0, unit="litre", supplier_id="SUP-001"),
    dict(id="PRD-003", name="Peynir",        category="süt",    stock_quantity=8,   low_threshold=15,  unit_price=220.0, unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-004", name="Mercimek",      category="tahıl",  stock_quantity=200, low_threshold=30,  unit_price=45.0,  unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-005", name="Organik Bal",   category="gıda",   stock_quantity=5,   low_threshold=10,  unit_price=350.0, unit="adet",  supplier_id="SUP-003"),
    dict(id="PRD-006", name="Biber",         category="sebze",  stock_quantity=12,  low_threshold=20,  unit_price=18.0,  unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-007", name="Patates",       category="sebze",  stock_quantity=300, low_threshold=50,  unit_price=12.0,  unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-008", name="Soğan",         category="sebze",  stock_quantity=7,   low_threshold=30,  unit_price=8.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-009", name="Salatalık",     category="sebze",  stock_quantity=0,   low_threshold=20,  unit_price=15.0,  unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-010", name="Nohut",         category="tahıl",  stock_quantity=150, low_threshold=25,  unit_price=38.0,  unit="kg",    supplier_id="SUP-001"),
]
for p in products:
    if add_if_not_exists(Product, **p):
        durum = "⚠️ KRİTİK" if p["stock_quantity"] <= p["low_threshold"] else "✅"
        print(f"  {durum} Ürün: {p['name']} (stok: {p['stock_quantity']} {p['unit']})")

# ── Siparişler ────────────────────────────────────────────────────────────────
orders = [
    dict(id="ORD-128", customer_name="Ahmet Yılmaz",  customer_phone="0532 111 2233",
         status="kargoda",       total_amount=650.0,
         tracking_number="TRK-4891", cargo_company="Yurtiçi Kargo"),

    dict(id="ORD-129", customer_name="Fatma Kaya",    customer_phone="0533 222 3344",
         status="beklemede",     total_amount=1200.0),

    dict(id="ORD-130", customer_name="Mehmet Demir",  customer_phone="0534 333 4455",
         status="hazirlaniyor",  total_amount=890.0),

    dict(id="ORD-131", customer_name="Ayşe Çelik",   customer_phone="0535 444 5566",
         status="teslim_edildi", total_amount=450.0,
         tracking_number="TRK-4880", cargo_company="Yurtiçi Kargo"),

    dict(id="ORD-132", customer_name="Ali Öztürk",   customer_phone="0536 555 6677",
         status="kargoda",       total_amount=2100.0,
         tracking_number="TRK-4895", cargo_company="Aras Kargo"),

    dict(id="ORD-133", customer_name="Zeynep Arslan", customer_phone="0537 666 7788",
         status="beklemede",     total_amount=320.0),
]
for o in orders:
    if add_if_not_exists(Order, **o):
        print(f"  📦 Sipariş: {o['id']} — {o['customer_name']} ({o['status']})")

# ── Başlangıç Bildirimleri ────────────────────────────────────────────────────
notifications = [
    dict(type="sabah_raporu",  title="☀️ Günlük Sabah Raporu",
         message="6 sipariş aktif, 4 ürün kritik stok seviyesinde. Günaydın!",
         priority="orta",  is_read=False),
    dict(type="stok_uyari",    title="⚠️ Kritik Stok: Organik Bal",
         message="Organik Bal stoğu kritik seviyede! Mevcut: 5 adet (Eşik: 10)",
         priority="yuksek", is_read=False),
    dict(type="stok_uyari",    title="⚠️ Kritik Stok: Salatalık",
         message="Salatalık stoğu tükendi! Mevcut: 0 kg",
         priority="kritik", is_read=False),
]
for n in notifications:
    obj = Notification(**n)
    db.add(obj)

db.commit()
db.close()

print("\n✅ Seed verisi başarıyla yüklendi!")
print("\n📋 Demo için hazır sorgular:")
print("  • 'ORD-128 nerede?'")
print("  • 'Organik Bal var mı?'")
print("  • 'Domates stoku nedir?'")
print("  • 'Bugünkü sipariş durumu nedir?'")
print("  • 'ORD-132 kargo durumunu öğrenebilir miyim?'")

