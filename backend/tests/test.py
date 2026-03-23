# backend/test_connection.py
from app.database import SessionLocal, engine
from app.models import Equipment
from sqlalchemy import inspect

def test_connection():
    """Тестируем подключение к БД"""
    try:
        # Пытаемся подключиться
        db = SessionLocal()
        
        # Проверяем, что можем выполнить простой запрос
        count = db.query(Equipment).count()
        print(f"✅ Successfully connected to database!")
        print(f"✅ Found {count} items in the database")
        
        # Проверяем структуру модели
        inspector = inspect(engine)
        actual_columns = [col['name'] for col in inspector.get_columns('equipment')]
        model_columns = [col.name for col in Equipment.__table__.columns]
        
        print("\n📊 Model columns:", model_columns)
        print("📊 Actual DB columns:", actual_columns)
        
        # Проверяем соответствие
        if set(model_columns) == set(actual_columns):
            print("✅ Model matches database structure!")
        else:
            print("⚠️ Model and database differ:")
            print(f"   In model but not in DB: {set(model_columns) - set(actual_columns)}")
            print(f"   In DB but not in model: {set(actual_columns) - set(model_columns)}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()