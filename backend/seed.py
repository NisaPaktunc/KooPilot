"""
KooPilot Demo Verisi — Genişletilmiş
─────────────────────────────────────
Çalıştır: python seed.py

Önceki seed.py'nin 3x büyütülmüş versiyonu.
KOBİ / kooperatif senaryosu: tarım, gıda, el sanatları.
"""

from database import engine, SessionLocal
from models import Base, Product, Order, OrderItem, Supplier, Notification

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
    dict(id="SUP-001", name="Anadolu Gıda AŞ",        email="siparis@anadolugida.com",      phone="0212 555 0001"),
    dict(id="SUP-002", name="Marmara Sebze Ltd",       email="info@marmarasebze.com",        phone="0216 555 0002"),
    dict(id="SUP-003", name="Ege Organik Tarım",       email="uretim@egeorganik.com",        phone="0232 555 0003"),
    dict(id="SUP-004", name="Karadeniz Fındık Koop.",  email="findik@karadenizkooperatif.com", phone="0462 555 0004"),
    dict(id="SUP-005", name="Güneydoğu Baharat San.",  email="info@gdbaharat.com.tr",        phone="0342 555 0005"),
    dict(id="SUP-006", name="Anadolu El Sanatları",    email="satis@anadoluelsanatlari.com",  phone="0312 555 0006"),
    dict(id="SUP-007", name="Trakya Hububat Ltd",      email="siparis@trakyahububat.com",    phone="0282 555 0007"),
]
for s in suppliers:
    if add_if_not_exists(Supplier, **s):
        print(f"  ✅ Tedarikçi: {s['name']}")

# ── Ürünler ───────────────────────────────────────────────────────────────────
# Kasıtlı olarak bazıları kritik / tükenen stokta
products = [
    # Sebze
    dict(id="PRD-001", name="Domates",             category="sebze",      stock_quantity=48,  low_threshold=50,  unit_price=25.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-006", name="Biber",               category="sebze",      stock_quantity=12,  low_threshold=20,  unit_price=18.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-007", name="Patates",             category="sebze",      stock_quantity=300, low_threshold=50,  unit_price=12.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-008", name="Soğan",               category="sebze",      stock_quantity=7,   low_threshold=30,  unit_price=8.0,    unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-009", name="Salatalık",           category="sebze",      stock_quantity=0,   low_threshold=20,  unit_price=15.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-016", name="Patlıcan",            category="sebze",      stock_quantity=55,  low_threshold=25,  unit_price=22.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-017", name="Kabak",               category="sebze",      stock_quantity=6,   low_threshold=20,  unit_price=14.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-018", name="Ispanak",             category="sebze",      stock_quantity=0,   low_threshold=15,  unit_price=20.0,   unit="kg",    supplier_id="SUP-002"),
    dict(id="PRD-019", name="Maydanoz",            category="sebze",      stock_quantity=30,  low_threshold=10,  unit_price=10.0,   unit="demet", supplier_id="SUP-002"),
    dict(id="PRD-020", name="Marul",               category="sebze",      stock_quantity=4,   low_threshold=20,  unit_price=12.0,   unit="adet",  supplier_id="SUP-002"),

    # Yağ & Süt
    dict(id="PRD-002", name="Zeytinyağı",          category="yağ",        stock_quantity=120, low_threshold=20,  unit_price=180.0,  unit="litre", supplier_id="SUP-001"),
    dict(id="PRD-003", name="Peynir",              category="süt",        stock_quantity=8,   low_threshold=15,  unit_price=220.0,  unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-021", name="Kaşar Peyniri",       category="süt",        stock_quantity=3,   low_threshold=10,  unit_price=280.0,  unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-022", name="Tereyağı",            category="süt",        stock_quantity=45,  low_threshold=15,  unit_price=320.0,  unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-023", name="Yoğurt",              category="süt",        stock_quantity=80,  low_threshold=20,  unit_price=60.0,   unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-024", name="Ayçiçek Yağı",        category="yağ",        stock_quantity=200, low_threshold=30,  unit_price=85.0,   unit="litre", supplier_id="SUP-001"),

    # Tahıl & Baklagil
    dict(id="PRD-004", name="Mercimek",            category="tahıl",      stock_quantity=200, low_threshold=30,  unit_price=45.0,   unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-010", name="Nohut",               category="tahıl",      stock_quantity=150, low_threshold=25,  unit_price=38.0,   unit="kg",    supplier_id="SUP-001"),
    dict(id="PRD-025", name="Buğday Unu",          category="tahıl",      stock_quantity=500, low_threshold=80,  unit_price=22.0,   unit="kg",    supplier_id="SUP-007"),
    dict(id="PRD-026", name="Pirinç",              category="tahıl",      stock_quantity=9,   low_threshold=30,  unit_price=55.0,   unit="kg",    supplier_id="SUP-007"),
    dict(id="PRD-027", name="Kuru Fasulye",        category="tahıl",      stock_quantity=170, low_threshold=30,  unit_price=48.0,   unit="kg",    supplier_id="SUP-007"),
    dict(id="PRD-028", name="Bulgur",              category="tahıl",      stock_quantity=260, low_threshold=40,  unit_price=30.0,   unit="kg",    supplier_id="SUP-007"),

    # Organik & Arıcılık
    dict(id="PRD-005", name="Organik Bal",         category="organik",    stock_quantity=5,   low_threshold=10,  unit_price=350.0,  unit="adet",  supplier_id="SUP-003"),
    dict(id="PRD-011", name="Organik Zeytinyağı",  category="organik",    stock_quantity=30,  low_threshold=12,  unit_price=240.0,  unit="litre", supplier_id="SUP-003"),
    dict(id="PRD-029", name="Polen",               category="organik",    stock_quantity=2,   low_threshold=8,   unit_price=420.0,  unit="adet",  supplier_id="SUP-003"),
    dict(id="PRD-030", name="Propolis",            category="organik",    stock_quantity=18,  low_threshold=5,   unit_price=280.0,  unit="adet",  supplier_id="SUP-003"),

    # Fındık & Kuruyemiş
    dict(id="PRD-012", name="Fındık",              category="kuruyemiş",  stock_quantity=75,  low_threshold=20,  unit_price=180.0,  unit="kg",    supplier_id="SUP-004"),
    dict(id="PRD-013", name="Fındık Ezmesi",       category="kuruyemiş",  stock_quantity=40,  low_threshold=10,  unit_price=320.0,  unit="kg",    supplier_id="SUP-004"),
    dict(id="PRD-031", name="Ceviz",               category="kuruyemiş",  stock_quantity=0,   low_threshold=15,  unit_price=210.0,  unit="kg",    supplier_id="SUP-004"),
    dict(id="PRD-032", name="Badem",               category="kuruyemiş",  stock_quantity=6,   low_threshold=12,  unit_price=260.0,  unit="kg",    supplier_id="SUP-004"),

    # Baharat
    dict(id="PRD-014", name="Kırmızı Pul Biber",  category="baharat",    stock_quantity=60,  low_threshold=15,  unit_price=120.0,  unit="kg",    supplier_id="SUP-005"),
    dict(id="PRD-015", name="Kimyon",              category="baharat",    stock_quantity=25,  low_threshold=10,  unit_price=150.0,  unit="kg",    supplier_id="SUP-005"),
    dict(id="PRD-033", name="Pul Biber",           category="baharat",    stock_quantity=50,  low_threshold=15,  unit_price=110.0,  unit="kg",    supplier_id="SUP-005"),
    dict(id="PRD-034", name="Kekik",               category="baharat",    stock_quantity=3,   low_threshold=10,  unit_price=130.0,  unit="kg",    supplier_id="SUP-005"),
    dict(id="PRD-035", name="Nane",                category="baharat",    stock_quantity=40,  low_threshold=10,  unit_price=90.0,   unit="kg",    supplier_id="SUP-005"),

    # El Sanatları
    dict(id="PRD-036", name="El Dokuması Kilim",   category="el sanatı",  stock_quantity=12,  low_threshold=3,   unit_price=1800.0, unit="adet",  supplier_id="SUP-006"),
    dict(id="PRD-037", name="Seramik Tabak Seti",  category="el sanatı",  stock_quantity=0,   low_threshold=5,   unit_price=450.0,  unit="set",   supplier_id="SUP-006"),
    dict(id="PRD-038", name="Ahşap Kaşık Seti",   category="el sanatı",  stock_quantity=35,  low_threshold=8,   unit_price=180.0,  unit="set",   supplier_id="SUP-006"),
    dict(id="PRD-039", name="Bakır Cezve",         category="el sanatı",  stock_quantity=7,   low_threshold=5,   unit_price=650.0,  unit="adet",  supplier_id="SUP-006"),
    dict(id="PRD-040", name="Hasır Sepet",         category="el sanatı",  stock_quantity=2,   low_threshold=6,   unit_price=220.0,  unit="adet",  supplier_id="SUP-006"),
]
for p in products:
    if add_if_not_exists(Product, **p):
        durum = "⚠️ KRİTİK" if p["stock_quantity"] <= p["low_threshold"] else "✅"
        print(f"  {durum} Ürün: {p['name']} (stok: {p['stock_quantity']} {p['unit']})")

# ── Siparişler ────────────────────────────────────────────────────────────────
orders = [
    # Orijinal siparişler
    dict(id="ORD-128", customer_name="Ahmet Yılmaz",     customer_phone="0532 111 2233", customer_email="ahmet.yilmaz@gmail.com",
         status="kargoda",       total_amount=650.0,  tracking_number="TRK-4891", cargo_company="Yurtiçi Kargo",
         notes="Kapıda teslim lütfen"),
    dict(id="ORD-129", customer_name="Fatma Kaya",       customer_phone="0533 222 3344", customer_email="fatma.kaya@hotmail.com",
         status="beklemede",     total_amount=1200.0),
    dict(id="ORD-130", customer_name="Mehmet Demir",     customer_phone="0534 333 4455", customer_email="m.demir@outlook.com",
         status="hazirlaniyor",  total_amount=890.0),
    dict(id="ORD-131", customer_name="Ayşe Çelik",       customer_phone="0535 444 5566", customer_email="aysecelik34@gmail.com",
         status="teslim_edildi", total_amount=450.0,  tracking_number="TRK-4880", cargo_company="Yurtiçi Kargo"),
    dict(id="ORD-132", customer_name="Ali Öztürk",       customer_phone="0536 555 6677", customer_email="aliozturk@gmail.com",
         status="kargoda",       total_amount=2100.0, tracking_number="TRK-4895", cargo_company="Aras Kargo"),
    dict(id="ORD-133", customer_name="Zeynep Arslan",    customer_phone="0537 666 7788", customer_email="zarslan@gmail.com",
         status="beklemede",     total_amount=320.0),

    # Yeni siparişler
    dict(id="ORD-134", customer_name="Hasan Koçak",      customer_phone="0538 777 8899", customer_email="hkoçak@gmail.com",
         status="hazirlaniyor",  total_amount=740.0,
         notes="Faturayı faks çekin"),
    dict(id="ORD-135", customer_name="Elif Şahin",       customer_phone="0539 888 9900", customer_email="elifşahin@icloud.com",
         status="kargoda",       total_amount=520.0,  tracking_number="TRK-4901", cargo_company="MNG Kargo"),
    dict(id="ORD-136", customer_name="Mustafa Erdoğan",  customer_phone="0530 999 0011", customer_email="merdogan@gmail.com",
         status="teslim_edildi", total_amount=1650.0, tracking_number="TRK-4876", cargo_company="Aras Kargo"),
    dict(id="ORD-137", customer_name="Hatice Yıldız",    customer_phone="0531 000 1122", customer_email="hatice.yildiz@outlook.com",
         status="iptal",         total_amount=280.0,
         notes="Müşteri vazgeçti — iade işlemi tamamlandı"),
    dict(id="ORD-138", customer_name="İbrahim Can",      customer_phone="0532 111 3344", customer_email="ibrahimcan@gmail.com",
         status="beklemede",     total_amount=3400.0,
         notes="Toplu sipariş — fatura gerekli"),
    dict(id="ORD-139", customer_name="Selin Aksoy",      customer_phone="0533 222 4455", customer_email="selina@gmail.com",
         status="hazirlaniyor",  total_amount=960.0),
    dict(id="ORD-140", customer_name="Kemal Bulut",      customer_phone="0534 333 5566", customer_email="kemalbulut@hotmail.com",
         status="kargoda",       total_amount=1120.0, tracking_number="TRK-4908", cargo_company="PTT Kargo"),
    dict(id="ORD-141", customer_name="Nur Çetin",        customer_phone="0535 444 6677", customer_email="nurcetin@gmail.com",
         status="teslim_edildi", total_amount=850.0,  tracking_number="TRK-4890", cargo_company="Yurtiçi Kargo"),
    dict(id="ORD-142", customer_name="Burak Arslan",     customer_phone="0536 555 7788", customer_email="burak.arslan@gmail.com",
         status="hazirlaniyor",  total_amount=430.0),
    dict(id="ORD-143", customer_name="Gülşen Özer",      customer_phone="0537 666 8899", customer_email="gulsenoz@gmail.com",
         status="kargoda",       total_amount=2750.0, tracking_number="TRK-4915", cargo_company="Aras Kargo",
         notes="Hafta sonu teslimat"),
    dict(id="ORD-144", customer_name="Tarık Doğan",      customer_phone="0538 777 9900", customer_email="tarik.dogan@gmail.com",
         status="beklemede",     total_amount=560.0),
    dict(id="ORD-145", customer_name="Merve Yılmaz",     customer_phone="0539 888 0011", customer_email="merve.y@gmail.com",
         status="teslim_edildi", total_amount=990.0,  tracking_number="TRK-4870", cargo_company="MNG Kargo"),
    dict(id="ORD-146", customer_name="Cemil Kara",       customer_phone="0530 999 1122", customer_email="cemilkara@outlook.com",
         status="hazirlaniyor",  total_amount=1350.0),
    dict(id="ORD-147", customer_name="Pınar Güneş",      customer_phone="0531 000 2233", customer_email="pinargunes@gmail.com",
         status="kargoda",       total_amount=670.0,  tracking_number="TRK-4920", cargo_company="Yurtiçi Kargo"),
]

for o in orders:
    if add_if_not_exists(Order, **o):
        print(f"  📦 Sipariş: {o['id']} — {o['customer_name']} ({o['status']}) {o['total_amount']} ₺")

# ── Sipariş Kalemleri ─────────────────────────────────────────────────────────
order_items = [
    # ORD-128: Ahmet Yılmaz
    dict(order_id="ORD-128", product_id="PRD-001", quantity=10, unit_price=25.0),
    dict(order_id="ORD-128", product_id="PRD-003", quantity=2,  unit_price=220.0),

    # ORD-129: Fatma Kaya
    dict(order_id="ORD-129", product_id="PRD-002", quantity=4,  unit_price=180.0),
    dict(order_id="ORD-129", product_id="PRD-005", quantity=2,  unit_price=350.0),
    dict(order_id="ORD-129", product_id="PRD-004", quantity=5,  unit_price=45.0),

    # ORD-130: Mehmet Demir
    dict(order_id="ORD-130", product_id="PRD-012", quantity=3,  unit_price=180.0),
    dict(order_id="ORD-130", product_id="PRD-013", quantity=1,  unit_price=320.0),

    # ORD-131: Ayşe Çelik
    dict(order_id="ORD-131", product_id="PRD-007", quantity=20, unit_price=12.0),
    dict(order_id="ORD-131", product_id="PRD-008", quantity=5,  unit_price=8.0),

    # ORD-132: Ali Öztürk
    dict(order_id="ORD-132", product_id="PRD-036", quantity=1,  unit_price=1800.0),
    dict(order_id="ORD-132", product_id="PRD-039", quantity=2,  unit_price=650.0),

    # ORD-134: Hasan Koçak
    dict(order_id="ORD-134", product_id="PRD-010", quantity=8,  unit_price=38.0),
    dict(order_id="ORD-134", product_id="PRD-025", quantity=20, unit_price=22.0),

    # ORD-135: Elif Şahin
    dict(order_id="ORD-135", product_id="PRD-011", quantity=2,  unit_price=240.0),
    dict(order_id="ORD-135", product_id="PRD-030", quantity=1,  unit_price=280.0),

    # ORD-136: Mustafa Erdoğan
    dict(order_id="ORD-136", product_id="PRD-036", quantity=1,  unit_price=1800.0),
    dict(order_id="ORD-136", product_id="PRD-038", quantity=3,  unit_price=180.0),

    # ORD-138: İbrahim Can (toplu)
    dict(order_id="ORD-138", product_id="PRD-002", quantity=10, unit_price=180.0),
    dict(order_id="ORD-138", product_id="PRD-004", quantity=20, unit_price=45.0),
    dict(order_id="ORD-138", product_id="PRD-025", quantity=30, unit_price=22.0),

    # ORD-139: Selin Aksoy
    dict(order_id="ORD-139", product_id="PRD-014", quantity=3,  unit_price=120.0),
    dict(order_id="ORD-139", product_id="PRD-015", quantity=2,  unit_price=150.0),
    dict(order_id="ORD-139", product_id="PRD-033", quantity=3,  unit_price=110.0),

    # ORD-140: Kemal Bulut
    dict(order_id="ORD-140", product_id="PRD-016", quantity=20, unit_price=22.0),
    dict(order_id="ORD-140", product_id="PRD-019", quantity=30, unit_price=10.0),

    # ORD-141: Nur Çetin
    dict(order_id="ORD-141", product_id="PRD-023", quantity=10, unit_price=60.0),
    dict(order_id="ORD-141", product_id="PRD-022", quantity=1,  unit_price=320.0),

    # ORD-143: Gülşen Özer
    dict(order_id="ORD-143", product_id="PRD-036", quantity=1,  unit_price=1800.0),
    dict(order_id="ORD-143", product_id="PRD-037", quantity=2,  unit_price=450.0),

    # ORD-145: Merve Yılmaz
    dict(order_id="ORD-145", product_id="PRD-005", quantity=2,  unit_price=350.0),
    dict(order_id="ORD-145", product_id="PRD-029", quantity=1,  unit_price=420.0),

    # ORD-146: Cemil Kara
    dict(order_id="ORD-146", product_id="PRD-028", quantity=20, unit_price=30.0),
    dict(order_id="ORD-146", product_id="PRD-027", quantity=10, unit_price=48.0),
    dict(order_id="ORD-146", product_id="PRD-026", quantity=5,  unit_price=55.0),

    # ORD-147: Pınar Güneş
    dict(order_id="ORD-147", product_id="PRD-035", quantity=3,  unit_price=90.0),
    dict(order_id="ORD-147", product_id="PRD-034", quantity=3,  unit_price=130.0),
]

for item in order_items:
    obj = OrderItem(**item)
    db.add(obj)
print(f"\n  ✅ {len(order_items)} sipariş kalemi eklendi")

# ── Bildirimler ───────────────────────────────────────────────────────────────
notifications = [
    # Orijinaller
    dict(type="sabah_raporu",  title="☀️ Günlük Sabah Raporu",
         message="6 sipariş aktif, 4 ürün kritik stok seviyesinde. Günaydın!",
         priority="orta", is_read=False),
    dict(type="stok_uyari",    title="⚠️ Kritik Stok: Organik Bal",
         message="Organik Bal stoğu kritik seviyede! Mevcut: 5 adet (Eşik: 10). SUP-003 Ege Organik Tarım ile iletişime geçin.",
         priority="yuksek", is_read=False),
    dict(type="stok_uyari",    title="🚨 Stok Tükendi: Salatalık",
         message="Salatalık stoğu tamamen tükendi! Mevcut: 0 kg. Acil sipariş verilmeli.",
         priority="kritik", is_read=False),

    # Yeni stok uyarıları
    dict(type="stok_uyari", title="⚠️ Kritik Stok: Kaşar Peyniri",
         message="Kaşar Peyniri stoğu kritik! Mevcut: 3 kg (Eşik: 10 kg). Anadolu Gıda AŞ'ye sipariş verilmesi öneriliyor.",
         priority="yuksek", is_read=False),
    dict(type="stok_uyari", title="⚠️ Kritik Stok: Polen",
         message="Polen stoğu kritik! Mevcut: 2 adet (Eşik: 8). Ege Organik Tarım'ı arayın.",
         priority="yuksek", is_read=False),
    dict(type="stok_uyari", title="🚨 Stok Tükendi: Ceviz",
         message="Ceviz stoğu tamamen bitti! Mevcut: 0 kg. Karadeniz Fındık Koop. ile acil iletişim kurun.",
         priority="kritik", is_read=False),
    dict(type="stok_uyari", title="🚨 Stok Tükendi: Seramik Tabak Seti",
         message="Seramik Tabak Seti stokta yok! Mevcut: 0 set. Bu ürüne aktif talep var (ORD-143).",
         priority="kritik", is_read=False),
    dict(type="stok_uyari", title="⚠️ Kritik Stok: Kabak",
         message="Kabak stoğu düşük. Mevcut: 6 kg (Eşik: 20 kg). Hafta sonu büyük sipariş gelmeden temin edilmeli.",
         priority="yuksek", is_read=False),
    dict(type="stok_uyari", title="🚨 Stok Tükendi: Ispanak",
         message="Ispanak stoğu bitti! Mevcut: 0 kg. Haftalık sepet abonelerini bilgilendirin.",
         priority="kritik", is_read=False),
    dict(type="stok_uyari", title="⚠️ Kritik Stok: Soğan",
         message="Soğan stoğu alarm seviyesinde. Mevcut: 7 kg (Eşik: 30 kg). Bu haftaki siparişler karşılanamayabilir.",
         priority="yuksek", is_read=False),
    dict(type="stok_uyari", title="⚠️ Düşük Stok: Hasır Sepet",
         message="Hasır Sepet stoğu 2 adede düştü (Eşik: 6). Anadolu El Sanatları'ndan temin edin.",
         priority="orta", is_read=False),

    # Kargo bildirimleri
    dict(type="kargo_gecikme", title="🚚 Kargo Gecikmesi: ORD-132 (Ali Öztürk)",
         message="TRK-4895 (Aras Kargo) hava koşulları nedeniyle gecikti. Tahmini teslim 2 gün ertelenmiş. Müşteri bilgilendirilmeli.",
         priority="yuksek", is_read=False),
    dict(type="kargo_gecikme", title="🚚 Kargo Gecikmesi: ORD-143 (Gülşen Özer)",
         message="TRK-4915 (Aras Kargo) depo kapasitesi nedeniyle gecikti. Müşteri hafta sonu teslim istedi, gecikmeden haberdar değil.",
         priority="yuksek", is_read=False),

    # Yeni sipariş bildirimleri
    dict(type="yeni_siparis", title="🆕 Yeni Sipariş: ORD-138 (İbrahim Can)",
         message="3.400 ₺ tutarında toplu sipariş alındı. Fatura kesilmesi gerekiyor. Stok kontrolü yapıldı, tüm ürünler mevcut.",
         priority="yuksek", is_read=False),
    dict(type="yeni_siparis", title="🆕 Yeni Sipariş: ORD-144 (Tarık Doğan)",
         message="560 ₺ tutarında sipariş beklemede. Hazırlık onayı bekleniyor.",
         priority="orta", is_read=True),
    dict(type="yeni_siparis", title="🆕 Yeni Sipariş: ORD-147 (Pınar Güneş)",
         message="Baharat siparişi alındı. Kargo şubesi için paketleme başlatılabilir.",
         priority="orta", is_read=True),

    # Genel
    dict(type="genel", title="💡 Haftalık Satış Özeti",
         message="Bu hafta 20 sipariş, toplam 18.430 ₺ ciro. En çok satan: Zeytinyağı (18 litre), Fındık (12 kg), Organik Bal (7 adet).",
         priority="dusuk", is_read=True),
    dict(type="genel", title="📊 Aylık Stok Analizi Hazır",
         message="Nisan ayı stok raporu: 8 ürün kritik eşiğin altında. Salatalık, Ispanak ve Ceviz'de tükenme yaşandı. Tedarikçi görüşmeleri planlanmalı.",
         priority="orta", is_read=True),
    dict(type="sabah_raporu", title="☀️ Sabah Raporu — Bugün",
         message="Bugün 12 aktif sipariş, 9 ürün kritik stokta, 2 kargoda gecikme var. En önemli eylem: Ceviz ve Ispanak için acil tedarik siparişi.",
         priority="yuksek", is_read=False),
]

for n in notifications:
    obj = Notification(**n)
    db.add(obj)
print(f"  ✅ {len(notifications)} bildirim eklendi")

db.commit()
db.close()

print("\n✅ Genişletilmiş seed verisi başarıyla yüklendi!")
print(f"\n📊 Özet:")
print(f"  • {len(suppliers)} tedarikçi")
print(f"  • {len(products)} ürün ({sum(1 for p in products if p['stock_quantity'] <= p['low_threshold'])} kritik/tükenen)")
print(f"  • {len(orders)} sipariş")
print(f"  • {len(order_items)} sipariş kalemi")
print(f"  • {len(notifications)} bildirim")
print("\n📋 Demo için örnek sorgular:")
print("  • 'ORD-143 siparişinin durumu nedir?'")
print("  • 'Hangi ürünlerin stoğu bitti?'")
print("  • 'Ispanak var mı?'")
print("  • 'Ali Öztürk'ün kargosu nerede?'")
print("  • 'Bugünkü geciken kargolar hangileri?'")
print("  • 'Seramik tabak seti kaçtan satıyor?'")
print("  • 'El sanatları kategorisinde hangi ürünler var?'")
print("  • 'Aras Kargo ile giden siparişler?'")