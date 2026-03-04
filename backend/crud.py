from sqlalchemy.orm import Session
from sqlalchemy import and_
import models
import schemas
from typing import List, Optional

# Menu Category CRUD
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MenuCategory).order_by(models.MenuCategory.display_order).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int):
    return db.query(models.MenuCategory).filter(models.MenuCategory.id == category_id).first()

def create_category(db: Session, category: schemas.MenuCategoryCreate):
    db_category = models.MenuCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Menu Item CRUD
def get_menu_items(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None):
    query = db.query(models.MenuItem)
    if category_id:
        query = query.filter(models.MenuItem.category_id == category_id)
    return query.order_by(models.MenuItem.display_order).offset(skip).limit(limit).all()

def get_menu_item(db: Session, item_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()

def create_menu_item(db: Session, item: schemas.MenuItemCreate):
    db_item = models.MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_menu_item_availability(db: Session, item_id: int, is_available: bool):
    db_item = get_menu_item(db, item_id)
    if db_item:
        db_item.is_available = is_available
        db.commit()
        db.refresh(db_item)
    return db_item

# Order CRUD
def create_order(db: Session, order: schemas.OrderCreate):
    # Calculate totals and create order
    total_amount = 0
    order_items = []
    
    for item in order.items:
        menu_item = get_menu_item(db, item.menu_item_id)
        if menu_item and menu_item.is_available:
            subtotal = menu_item.price * item.quantity
            total_amount += subtotal
            order_items.append({
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": menu_item.price,
                "subtotal": subtotal,
                "notes": item.notes
            })
    
    db_order = models.Order(
        table_number=order.table_number,
        customer_name=order.customer_name,
        waiter_name=order.waiter_name,
        special_instructions=order.special_instructions,
        total_amount=total_amount
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items
    for item_data in order_items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status: str):
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order