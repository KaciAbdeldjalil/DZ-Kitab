from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

with open("db_report.txt", "w") as f:
    f.write(f"Testing connection to: {DATABASE_URL}\n")
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        f.write(f"Tables found: {tables}\n")
        
        for table in ['announcements', 'conversations', 'messages', 'users', 'books']:
            if table in tables:
                columns = [c['name'] for c in inspector.get_columns(table)]
                f.write(f"Table '{table}' columns: {columns}\n")
            else:
                f.write(f"CRITICAL: Table '{table}' NOT FOUND!\n")
    except Exception as e:
        f.write(f"Database connection error: {str(e)}\n")
