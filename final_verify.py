import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'messages'"))
        cols = [r[0] for r in res.fetchall()]
        if 'conversation_id' in cols and 'status' in cols and 'read_at' in cols:
            print("VERIFICATION_RESULT:SUCCESS")
            print(f"Columns: {','.join(cols)}")
        else:
            print("VERIFICATION_RESULT:FAILURE")
            print(f"Missing columns. Found: {','.join(cols)}")
except Exception as e:
    print(f"VERIFICATION_RESULT:ERROR:{str(e)}")
