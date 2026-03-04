from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Menu Category Schemas
class MenuCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    display_order: Optional[int] = 0

class MenuCategoryCreate(MenuCategoryBase):
    pass

class MenuCategory(MenuCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Menu Item Schemas
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    image_url: Optional[str] = None
    is_available: Optional[bool] = True
    preparation_time: Optional[int] = None
    display_order: Optional[int] = 0

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[MenuCategory] = None
    
    class Config:
        from_attributes = True

# Order Item Schemas
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    notes: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    subtotal: float
    status: str
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    table_number: int
    customer_name: Optional[str] = None
    waiter_name: Optional[str] = None
    special_instructions: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    status: str
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItem] = []
    
    class Config:
        from_attributes = True