from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")
print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    for table in ['announcements', 'conversations', 'messages', 'users', 'books']:
        if table in tables:
            columns = [c['name'] for c in inspector.get_columns(table)]
            print(f"Table '{table}' columns: {columns}")
        else:
            print(f"CRITICAL: Table '{table}' NOT FOUND!")
            
except Exception as e:
    print(f"Database connection error: {e}")
