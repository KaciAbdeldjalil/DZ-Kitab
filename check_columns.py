import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'messages'"))
        columns = result.fetchall()
        print("Messages table columns:")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
            
except Exception as e:
    print(f"Error: {e}")
