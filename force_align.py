import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

print(f"Force aligning database at: {DATABASE_URL}")

sql = """
-- 1. Create enum if missing
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'messagestatus') THEN
        CREATE TYPE messagestatus AS ENUM ('sent', 'read', 'archived');
    END IF;
END $$;

-- 2. Clean messages table (Add missing, Drop wrong)
ALTER TABLE messages ADD COLUMN IF NOT EXISTS conversation_id INTEGER;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS status messagestatus DEFAULT 'sent';
ALTER TABLE messages ADD COLUMN IF NOT EXISTS read_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE messages DROP COLUMN IF EXISTS announcement_id;

-- 3. Add foreign key if missing
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_messages_conversation') THEN
        ALTER TABLE messages ADD CONSTRAINT fk_messages_conversation 
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 4. Update conversations if needed
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
"""

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("SQL applied successfully.")
    
    # Verify
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'messages'"))
        cols = [r[0] for r in res.fetchall()]
        print(f"Verified columns: {cols}")
        if 'conversation_id' in cols and 'status' in cols:
            print("SCHEMA IS NOW CORRECT.")
        else:
            print("SCHEMA IS STILL WRONG!")
            
except Exception as e:
    print(f"Critical Error: {e}")
