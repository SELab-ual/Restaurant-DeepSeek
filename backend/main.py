from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
import crud
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RMOS - Restaurant Menu & Ordering System",
    description="Sprint 1 Prototype: Digital Menu Foundation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": "RMOS Backend", "sprint": "1"}

# Menu Category Endpoints
@app.get("/api/categories", response_model=List[schemas.MenuCategory])
async def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

@app.get("/api/categories/{category_id}", response_model=schemas.MenuCategory)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@app.post("/api/categories", response_model=schemas.MenuCategory, status_code=status.HTTP_201_CREATED)
async def create_category(category: schemas.MenuCategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

# Menu Item Endpoints
@app.get("/api/menu-items", response_model=List[schemas.MenuItem])
async def get_menu_items(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return crud.get_menu_items(db, skip=skip, limit=limit, category_id=category_id)

@app.get("/api/menu-items/{item_id}", response_model=schemas.MenuItem)
async def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_menu_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_item

@app.post("/api/menu-items", response_model=schemas.MenuItem, status_code=status.HTTP_201_CREATED)
async def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    return crud.create_menu_item(db, item)

@app.patch("/api/menu-items/{item_id}/availability")
async def update_availability(item_id: int, is_available: bool, db: Session = Depends(get_db)):
    db_item = crud.update_menu_item_availability(db, item_id, is_available)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": f"Item {item_id} availability updated to {is_available}"}

# Order Endpoints
@app.post("/api/orders", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order)

@app.get("/api/orders", response_model=List[schemas.Order])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

@app.get("/api/orders/{order_id}", response_model=schemas.Order)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    valid_statuses = ["pending", "confirmed", "preparing", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    db_order = crud.update_order_status(db, order_id, status)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": f"Order {order_id} status updated to {status}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)