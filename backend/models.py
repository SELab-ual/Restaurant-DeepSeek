from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MenuCategory(Base):
    __tablename__ = "menu_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    preparation_time = Column(Integer)  # in minutes
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("MenuCategory", back_populates="items")
    order_items = relationship("OrderItem", back_populates="menu_item")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, nullable=False)
    customer_name = Column(String(100))
    waiter_name = Column(String(100))
    status = Column(String(50), default="pending")  # pending, confirmed, preparing, completed, cancelled
    total_amount = Column(Float, default=0)
    special_instructions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    notes = Column(Text)
    status = Column(String(50), default="pending")  # pending, accepted, rejected, ready, delivered
    
    order = relationship("Order", back_populates="items")
    menu_item = relationship("OrderItem", back_populates="menu_item")