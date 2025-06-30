from database import init_db
from models import Base

def test_database():
    print("Testing database connection and creating tables...")
    try:
        init_db()
        print("✅ Database connection successful and tables created!")
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    test_database() 