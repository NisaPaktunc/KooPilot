"""
Koopilot Akilli Analitik Motoru
────────────────────────────────
Veritabanina dogrudan baglanarak:
  - Gelir trendi ve anomali tespiti
  - Stok risk skorlama (0-100)
  - Musteri segmentasyonu (RFM benzeri)
  - Kategori performans matrisi
  - Otomatik aksiyonel oneriler
  - Tahmini gelir projeksiyonu

Kullanim:
  from services.analytics_engine import generate_insights
  result = generate_insights()
"""

from database import SessionLocal
from models import Product, Order, OrderItem, Supplier, Notification
from datetime import datetime, timedelta
from collections import defaultdict
import math


def generate_insights() -> dict:
    """Ana fonksiyon: tum analiz modullerini calistirir ve tek bir rapor doner."""
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        items = db.query(OrderItem).all()
        products = db.query(Product).all()
        suppliers = db.query(Supplier).all()
        notifications = db.query(Notification).all()

        # Her modulu calistir
        revenue = _revenue_analysis(orders, items, products)
        stock = _stock_risk_analysis(products, items)
        customers = _customer_analysis(orders, items, products)
        categories = _category_performance(items, products)
        actions = _generate_actions(revenue, stock, customers, categories, orders, products)
        health = _business_health_score(revenue, stock, orders, products)

        return {
            "generated_at": datetime.now().isoformat(),
            "health_score": health,
            "revenue": revenue,
            "stock_risks": stock,
            "customers": customers,
            "categories": categories,
            "actions": actions,
        }
    finally:
        db.close()


def generate_insights_text() -> str:
    """Gemini tool'u icin metin formatlı rapor."""
    data = generate_insights()
    lines = []

    # Saglik skoru
    h = data["health_score"]
    lines.append(f"## ISLETME SAGLIK SKORU: {h['score']}/100 ({h['grade']})")
    lines.append(f"Detay: Gelir={h['details']['revenue']}/25, Stok={h['details']['stock']}/25, "
                 f"Musteri={h['details']['customer']}/25, Operasyon={h['details']['operations']}/25")
    lines.append("")

    # Gelir ozeti
    r = data["revenue"]
    lines.append("## GELIR ANALIZI")
    lines.append(f"Toplam Ciro: {r['total_revenue']:,.0f} TL")
    lines.append(f"Ortalama Siparis: {r['avg_order']:,.0f} TL")
    lines.append(f"En yuksek siparis: {r['max_order']:,.0f} TL")
    lines.append(f"Gelir yogunlasma riski: En buyuk {r['concentration_top3_pct']:.0f}% (ilk 3 siparis)")
    lines.append("")

    # Stok riskleri
    lines.append(f"## STOK RISK ANALIZI ({len(data['stock_risks'])} urun)")
    for s in data["stock_risks"][:8]:
        lines.append(f"  {'!!' if s['risk_score']>=80 else '!'} {s['name']}: "
                     f"skor={s['risk_score']}/100, stok={s['current_stock']} {s['unit']}, "
                     f"tahmini tükenme={s['days_until_empty']} gun")
    lines.append("")

    # Musteri segmentleri
    lines.append("## MUSTERI SEGMENTASYONU")
    for seg in data["customers"]["segments"]:
        lines.append(f"  {seg['segment']}: {seg['count']} musteri, "
                     f"ort siparis={seg['avg_order']:,.0f} TL")
    lines.append(f"En degerli musteri: {data['customers']['top_customer']['name']} "
                 f"({data['customers']['top_customer']['total']:,.0f} TL)")
    lines.append("")

    # Kategori performansi
    lines.append("## KATEGORI PERFORMANSI")
    for c in data["categories"]:
        lines.append(f"  {c['category']}: {c['revenue']:,.0f} TL ciro, "
                     f"{c['items_sold']} adet, kar marji ~%{c['margin_estimate']:.0f}")
    lines.append("")

    # Aksiyonlar
    lines.append("## ONERILEN AKSIYONLAR")
    for i, a in enumerate(data["actions"], 1):
        lines.append(f"  {i}. [{a['priority']}] {a['action']}")
        lines.append(f"     Sebep: {a['reason']}")
        lines.append(f"     Beklenen etki: {a['impact']}")

    return "\n".join(lines)


# ── Gelir Analizi ─────────────────────────────────────────────────────────────

def _revenue_analysis(orders, items, products) -> dict:
    amounts = [o.total_amount or 0 for o in orders]
    total = sum(amounts)
    avg = total / len(amounts) if amounts else 0
    sorted_amounts = sorted(amounts, reverse=True)

    # Gelir yogunlasma (ilk 3 siparis toplam gelirin yuzde kaci)
    top3 = sum(sorted_amounts[:3]) if len(sorted_amounts) >= 3 else sum(sorted_amounts)
    concentration = (top3 / total * 100) if total > 0 else 0

    # Durum bazli gelir
    status_revenue = defaultdict(float)
    for o in orders:
        status_revenue[o.status] += (o.total_amount or 0)

    # Iptal kayip
    cancel_loss = status_revenue.get("iptal", 0)

    return {
        "total_revenue": total,
        "avg_order": avg,
        "max_order": max(amounts) if amounts else 0,
        "min_order": min(amounts) if amounts else 0,
        "order_count": len(orders),
        "concentration_top3_pct": concentration,
        "cancel_loss": cancel_loss,
        "status_revenue": dict(status_revenue),
        "revenue_at_risk": status_revenue.get("beklemede", 0),
    }


# ── Stok Risk Skorlama ───────────────────────────────────────────────────────

def _stock_risk_analysis(products, items) -> list:
    # Urun bazli satis miktari
    product_demand = defaultdict(int)
    for item in items:
        product_demand[item.product_id] += item.quantity

    risks = []
    for p in products:
        demand = product_demand.get(p.id, 0)
        daily_use = demand / 7  # 7 gunluk veri varsayimi

        # Risk skoru hesapla (0-100, yuksek = kotu)
        score = 0

        # Stok/esik orani (0-40 puan)
        if p.low_threshold > 0:
            ratio = p.stock_quantity / p.low_threshold
            if ratio == 0:
                score += 40
            elif ratio < 0.5:
                score += 35
            elif ratio < 1.0:
                score += 25
            elif ratio < 1.5:
                score += 10

        # Tükenme hizi (0-30 puan)
        days_left = int(p.stock_quantity / daily_use) if daily_use > 0 else 999
        if days_left == 0:
            score += 30
        elif days_left <= 3:
            score += 25
        elif days_left <= 7:
            score += 15
        elif days_left <= 14:
            score += 5

        # Talep yogunlugu (0-20 puan)
        if demand > 20:
            score += 20
        elif demand > 10:
            score += 12
        elif demand > 5:
            score += 6

        # Fiyat etkisi (pahali urunler tükenince kayip buyuk) (0-10 puan)
        if p.unit_price >= 300:
            score += 10
        elif p.unit_price >= 150:
            score += 6
        elif p.unit_price >= 50:
            score += 3

        risks.append({
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "current_stock": p.stock_quantity,
            "threshold": p.low_threshold,
            "unit": p.unit,
            "demand_total": demand,
            "daily_consumption": round(daily_use, 1),
            "days_until_empty": days_left if days_left < 999 else -1,
            "risk_score": min(100, score),
            "risk_level": "KRITIK" if score >= 70 else "YUKSEK" if score >= 50 else "ORTA" if score >= 30 else "DUSUK",
            "potential_loss": round(p.unit_price * max(0, p.low_threshold - p.stock_quantity), 2),
        })

    risks.sort(key=lambda x: x["risk_score"], reverse=True)
    return risks


# ── Musteri Segmentasyonu ─────────────────────────────────────────────────────

def _customer_analysis(orders, items, products) -> dict:
    customer_data = defaultdict(lambda: {"orders": 0, "total": 0.0, "items": 0})

    for o in orders:
        c = customer_data[o.customer_name]
        c["orders"] += 1
        c["total"] += (o.total_amount or 0)

    for item in items:
        # item -> order -> customer mapping
        for o in orders:
            if o.id == item.order_id:
                customer_data[o.customer_name]["items"] += item.quantity
                break

    # Segmentlere ayir
    segments = {"VIP": [], "Sadik": [], "Normal": [], "Yeni": []}
    for name, data in customer_data.items():
        avg = data["total"] / data["orders"] if data["orders"] > 0 else 0
        if data["total"] >= 2000 or data["orders"] >= 3:
            segments["VIP"].append({"name": name, **data, "avg": avg})
        elif data["total"] >= 1000:
            segments["Sadik"].append({"name": name, **data, "avg": avg})
        elif data["orders"] >= 2:
            segments["Normal"].append({"name": name, **data, "avg": avg})
        else:
            segments["Yeni"].append({"name": name, **data, "avg": avg})

    segment_summary = []
    for seg_name, members in segments.items():
        if members:
            segment_summary.append({
                "segment": seg_name,
                "count": len(members),
                "total_revenue": sum(m["total"] for m in members),
                "avg_order": sum(m["avg"] for m in members) / len(members),
                "members": [m["name"] for m in members],
            })

    # En degerli musteri
    top = max(customer_data.items(), key=lambda x: x[1]["total"])

    return {
        "total_customers": len(customer_data),
        "segments": segment_summary,
        "top_customer": {"name": top[0], "total": top[1]["total"], "orders": top[1]["orders"]},
        "avg_customer_value": sum(d["total"] for d in customer_data.values()) / len(customer_data) if customer_data else 0,
    }


# ── Kategori Performansi ─────────────────────────────────────────────────────

def _category_performance(items, products) -> list:
    product_map = {p.id: p for p in products}

    cat_data = defaultdict(lambda: {"revenue": 0.0, "items_sold": 0, "products": set(), "cost_approx": 0.0})

    for item in items:
        prod = product_map.get(item.product_id)
        if not prod:
            continue
        cat = prod.category or "genel"
        rev = item.quantity * item.unit_price
        cat_data[cat]["revenue"] += rev
        cat_data[cat]["items_sold"] += item.quantity
        cat_data[cat]["products"].add(prod.name)
        # Tahmini maliyet (basit: satis fiyatinin %60'i)
        cat_data[cat]["cost_approx"] += rev * 0.6

    result = []
    for cat, data in sorted(cat_data.items(), key=lambda x: x[1]["revenue"], reverse=True):
        margin = ((data["revenue"] - data["cost_approx"]) / data["revenue"] * 100) if data["revenue"] > 0 else 0
        result.append({
            "category": cat,
            "revenue": data["revenue"],
            "items_sold": data["items_sold"],
            "unique_products": len(data["products"]),
            "margin_estimate": margin,
            "avg_item_value": data["revenue"] / data["items_sold"] if data["items_sold"] > 0 else 0,
        })

    return result


# ── Isletme Saglik Skoru ──────────────────────────────────────────────────────

def _business_health_score(revenue, stock_risks, orders, products) -> dict:
    # 4 boyutlu skor (her biri max 25 puan, toplam 100)

    # 1. Gelir sagligi (25p)
    rev_score = 25
    if revenue["cancel_loss"] > revenue["total_revenue"] * 0.1:
        rev_score -= 8
    if revenue["concentration_top3_pct"] > 50:
        rev_score -= 5
    if revenue["avg_order"] < 500:
        rev_score -= 4
    rev_score = max(0, rev_score)

    # 2. Stok sagligi (25p)
    critical_count = sum(1 for s in stock_risks if s["risk_score"] >= 70)
    out_of_stock = sum(1 for s in stock_risks if s["current_stock"] == 0)
    stk_score = 25
    stk_score -= critical_count * 2
    stk_score -= out_of_stock * 3
    stk_score = max(0, stk_score)

    # 3. Musteri sagligi (25p)
    unique_customers = len(set(o.customer_name for o in orders))
    cust_score = min(25, unique_customers * 2)  # her musteri 2 puan

    # 4. Operasyon sagligi (25p)
    total = len(orders) if orders else 1
    delivered = sum(1 for o in orders if o.status == "teslim_edildi")
    cancelled = sum(1 for o in orders if o.status == "iptal")
    ops_score = 25
    if total > 0:
        delivery_rate = delivered / total
        cancel_rate = cancelled / total
        ops_score = int(25 * delivery_rate * (1 - cancel_rate))
    ops_score = max(0, min(25, ops_score))

    total_score = rev_score + stk_score + cust_score + ops_score
    grade = "A+" if total_score >= 90 else "A" if total_score >= 80 else "B" if total_score >= 65 else "C" if total_score >= 50 else "D"

    return {
        "score": total_score,
        "grade": grade,
        "details": {
            "revenue": rev_score,
            "stock": stk_score,
            "customer": cust_score,
            "operations": ops_score,
        }
    }


# ── Aksiyon Onerileri ─────────────────────────────────────────────────────────

def _generate_actions(revenue, stock_risks, customers, categories, orders, products) -> list:
    actions = []

    # Stok aksiyonlari
    critical_stocks = [s for s in stock_risks if s["risk_score"] >= 70]
    if critical_stocks:
        names = ", ".join(s["name"] for s in critical_stocks[:5])
        actions.append({
            "priority": "ACIL",
            "action": f"{len(critical_stocks)} urun icin acil tedarik siparisi ver",
            "reason": f"Kritik stok: {names}",
            "impact": f"Tahmini {sum(s['potential_loss'] for s in critical_stocks):,.0f} TL kayip onlenir",
            "category": "stok"
        })

    out_of_stock = [s for s in stock_risks if s["current_stock"] == 0]
    if out_of_stock:
        actions.append({
            "priority": "ACIL",
            "action": f"{len(out_of_stock)} tukenmis urun icin tedarikci ile iletisime gec",
            "reason": f"Tukenmis urunler satisi kaybettiriyor",
            "impact": "Musteri memnuniyeti ve satis kaybi engellenir",
            "category": "stok"
        })

    # Gelir aksiyonlari
    if revenue["revenue_at_risk"] > 0:
        actions.append({
            "priority": "YUKSEK",
            "action": f"Beklemedeki {revenue['revenue_at_risk']:,.0f} TL tutarindaki siparisleri hazirlamaya basla",
            "reason": "Bekleyen gelir realize edilmeli",
            "impact": f"{revenue['revenue_at_risk']:,.0f} TL gelir guvence altina alinir",
            "category": "gelir"
        })

    if revenue["cancel_loss"] > 0:
        actions.append({
            "priority": "ORTA",
            "action": "Iptal edilen siparislerin nedenlerini analiz et",
            "reason": f"{revenue['cancel_loss']:,.0f} TL iptal kaybi var",
            "impact": "Iptal oranini dusurerek gelir artisi saglanir",
            "category": "gelir"
        })

    # Kategori aksiyonlari
    if categories:
        top_cat = categories[0]
        actions.append({
            "priority": "ORTA",
            "action": f"'{top_cat['category']}' kategorisine yatirim yap, urun cesitliligini artir",
            "reason": f"En yuksek gelir getiren kategori: {top_cat['revenue']:,.0f} TL",
            "impact": "Guclu kategoride buyumeyi hizlandirir",
            "category": "strateji"
        })

    # Musteri aksiyonlari
    if customers["segments"]:
        vip = next((s for s in customers["segments"] if s["segment"] == "VIP"), None)
        if vip:
            actions.append({
                "priority": "ORTA",
                "action": f"VIP musterilere ({vip['count']} kisi) ozel kampanya hazirla",
                "reason": f"VIP segment toplam {vip['total_revenue']:,.0f} TL gelir sagliyor",
                "impact": "Sadakat artisi ve tekrar alis oraninda iyilesme",
                "category": "musteri"
            })

    return actions
