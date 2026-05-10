"""
Koopilot Tool Definitions & Handlers
─────────────────────────────────────
Backend-controlled tool'ların implementasyonları.
Tool routing ai_service.py içindeki rule-based router tarafından yapılır.

Mevcut tool'lar:
  - check_stock  →  Ürün stok bilgisini DB'den çeker
"""

from database import SessionLocal
from models import Product


# ── Tool Handlers ────────────────────────────────────────────────────────────

def check_stock(product_name: str) -> str:
    """
    Veritabanından ürün stok bilgisini çeker.
    Sonucu Gemini'ye context olarak verilecek string olarak döndürür.
    """
    db = SessionLocal()
    try:
        product = (
            db.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
            .first()
        )
        if product:
            stok_durumu = "mevcut" if product.stock_quantity > 0 else "tükendi"
            return (
                f"Ürün: {product.name} | "
                f"Kod: {product.id} | "
                f"Stok: {product.stock_quantity} adet ({stok_durumu})"
            )
        else:
            return f"'{product_name}' adlı ürün veritabanında bulunamadı."
    finally:
        db.close()


# ── Tool Dispatcher ──────────────────────────────────────────────────────────

TOOL_HANDLERS = {
    "check_stock": check_stock,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Verilen tool adını ve parametreleri alıp ilgili handler'ı çağırır.
    Bilinmeyen tool adı gelirse hata mesajı döndürür.
    """
    handler = TOOL_HANDLERS.get(tool_name)
    if handler:
        return handler(**tool_input)
    return f"Bilinmeyen araç: {tool_name}"
