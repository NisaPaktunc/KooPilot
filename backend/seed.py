from database import engine, SessionLocal
from models import Base, Product

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Seed products
products = [
    Product(id="PRD-001", name="Domates", stock_quantity=5),
    Product(id="PRD-002", name="Biber", stock_quantity=12),
    Product(id="PRD-003", name="Patates", stock_quantity=30),
    Product(id="PRD-004", name="Soğan", stock_quantity=8),
    Product(id="PRD-005", name="Salatalık", stock_quantity=0),
]

added = 0
for product in products:
    existing = db.query(Product).filter(Product.id == product.id).first()
    if not existing:
        db.add(product)
        added += 1
        print(f"  + Eklendi: {product.name} (stok: {product.stock_quantity})")
    else:
        print(f"  - Zaten mevcut: {existing.name}")

db.commit()
print(f"\nToplam {added} yeni ürün eklendi.")
