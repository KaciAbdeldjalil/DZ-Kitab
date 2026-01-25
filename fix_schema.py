import os
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

print(f"Applying schema fix to: {DATABASE_URL}")

fix_sql = """
-- 1. Add conversation_id to messages
ALTER TABLE messages ADD COLUMN IF NOT EXISTS conversation_id INTEGER;

-- 2. Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_messages_conversation') THEN
        ALTER TABLE messages ADD CONSTRAINT fk_messages_conversation 
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3. (Optional but good) Make it non-nullable if we can
-- For now, let's keep it nullable as there might be existing data.
-- But if the user is testing from scratch, it's better to be clean.
"""

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(fix_sql))
        conn.commit()
    print("Schema fix applied successfully!")
except Exception as e:
    print(f"Error applying fix: {e}")
