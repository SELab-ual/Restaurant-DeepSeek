import psycopg2
import os
import time
from sqlalchemy import create_engine, text
from database import Base, engine
import models

def wait_for_db():
    """Wait for database to be ready"""
    db_url = os.getenv("DATABASE_URL", "postgresql://rmos_user:rmos_password@db:5432/rmos_database")
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"⏳ Waiting for database... ({retries} retries left)")
            retries -= 1
            time.sleep(5)
    
    print("❌ Failed to connect to database")
    return False

def init_database():
    """Initialize database with sample data"""
    print("🚀 Initializing database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Import sample data
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Check if data already exists
    from models import MenuCategory, MenuItem
    
    if db.query(MenuCategory).count() == 0:
        # Create categories
        categories = [
            MenuCategory(name="Appetizers", description="Start your meal", display_order=1),
            MenuCategory(name="Main Courses", description="Signature dishes", display_order=2),
            MenuCategory(name="Desserts", description="Sweet endings", display_order=3),
            MenuCategory(name="Beverages", description="Drinks & refreshments", display_order=4),
        ]
        db.add_all(categories)
        db.commit()
        print("✅ Categories created")
        
        # Create menu items
        items = [
            # Appetizers
            MenuItem(name="Bruschetta", description="Toasted bread with tomatoes, garlic, and basil", price=8.99, category_id=1, preparation_time=10),
            MenuItem(name="Calamari", description="Fried squid with marinara sauce", price=12.99, category_id=1, preparation_time=15),
            MenuItem(name="Stuffed Mushrooms", description="Mushrooms filled with cheese and herbs", price=10.99, category_id=1, preparation_time=12),
            
            # Main Courses
            MenuItem(name="Grilled Salmon", description="Fresh salmon with lemon butter sauce", price=24.99, category_id=2, preparation_time=20),
            MenuItem(name="Ribeye Steak", description="12oz steak with mashed potatoes", price=32.99, category_id=2, preparation_time=25),
            MenuItem(name="Chicken Parmesan", description="Breaded chicken with marinara and mozzarella", price=18.99, category_id=2, preparation_time=22),
            MenuItem(name="Vegetable Pasta", description="Fresh vegetables with penne in pesto", price=16.99, category_id=2, preparation_time=18),
            
            # Desserts
            MenuItem(name="Tiramisu", description="Classic Italian dessert", price=7.99, category_id=3, preparation_time=5),
            MenuItem(name="Cheesecake", description="New York style with berry compote", price=8.99, category_id=3, preparation_time=5),
            MenuItem(name="Chocolate Lava Cake", description="Warm cake with molten center", price=9.99, category_id=3, preparation_time=8),
            
            # Beverages
            MenuItem(name="Soft Drinks", description="Coke, Sprite, Fanta", price=2.99, category_id=4, preparation_time=2),
            MenuItem(name="Fresh Juice", description="Orange, Apple, Carrot", price=4.99, category_id=4, preparation_time=3),
            MenuItem(name="Coffee", description="Fresh brewed", price=3.99, category_id=4, preparation_time=3),
            MenuItem(name="House Wine", description="Red or White", price=7.99, category_id=4, preparation_time=2),
        ]
        db.add_all(items)
        db.commit()
        print("✅ Menu items created")
    else:
        print("📊 Database already contains data")
    
    db.close()
    print("✅ Database initialization complete")

if __name__ == "__main__":
    if wait_for_db():
        init_database()
    else:
        print("❌ Cannot initialize database - exiting")
        exit(1)