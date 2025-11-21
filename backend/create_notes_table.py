"""Create notes_metadata table with all required columns"""
from dotenv import load_dotenv
import psycopg
import os

load_dotenv()

conn_string = os.getenv('POSTGRES_CONNECTION_STRING')
if not conn_string:
    print("❌ POSTGRES_CONNECTION_STRING not found in .env")
    exit(1)

try:
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            # Check existing tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            print("📋 Existing tables:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Create notes_metadata table if it doesn't exist
            print("\n🔨 Creating notes_metadata table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes_metadata (
                    id SERIAL PRIMARY KEY,
                    file_id VARCHAR(100) UNIQUE NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    stored_filename VARCHAR(255),
                    subject VARCHAR(100),
                    topic VARCHAR(100),
                    file_size INTEGER,
                    file_path TEXT,
                    chunk_count INTEGER,
                    upload_date TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_id 
                ON notes_metadata(file_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic 
                ON notes_metadata(topic)
            """)
            
            conn.commit()
            print("✅ notes_metadata table created successfully!")
            print("   - All columns including stored_filename and file_size")
            print("   - Indexes created on file_id and topic")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

