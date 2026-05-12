from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id    = Column(String, primary_key=True)   # SUP-001
    name  = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)

    products = relationship("Product", back_populates="supplier")


class Product(Base):
    __tablename__ = "products"

    id              = Column(String, primary_key=True)   # PRD-001
    name            = Column(String, nullable=False)
    category        = Column(String, default="genel")
    stock_quantity  = Column(Integer, default=0)
    low_threshold   = Column(Integer, default=10)        # Bu altı = kritik
    unit_price      = Column(Float, default=0.0)
    unit            = Column(String, default="adet")     # kg / adet / litre
    supplier_id     = Column(String, ForeignKey("suppliers.id"), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    supplier    = relationship("Supplier", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id              = Column(String, primary_key=True)   # ORD-128
    customer_name   = Column(String, nullable=False)
    customer_phone  = Column(String)
    customer_email  = Column(String)
    status          = Column(String, default="beklemede")
    # beklemede | hazirlaniyor | kargoda | teslim_edildi | iptal
    total_amount    = Column(Float, default=0.0)
    tracking_number = Column(String)
    cargo_company   = Column(String)
    notes           = Column(Text)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    order_id   = Column(String, ForeignKey("orders.id"))
    product_id = Column(String, ForeignKey("products.id"))
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    type       = Column(String, default="genel")
    # stok_uyari | kargo_gecikme | yeni_siparis | sabah_raporu | genel
    title      = Column(String, nullable=False)
    message    = Column(Text)
    priority   = Column(String, default="orta")
    # dusuk | orta | yuksek | kritik
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    role       = Column(String)   # user | assistant
    content    = Column(Text)
    timestamp  = Column(DateTime(timezone=True), server_default=func.now())
