"""Create syllabus table in PostgreSQL"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def create_syllabus_table():
    conn_string = os.getenv('POSTGRES_CONNECTION_STRING')
    if not conn_string:
        print("❌ POSTGRES_CONNECTION_STRING not found in .env")
        return
    
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM pg_tables 
                        WHERE schemaname = 'public' 
                        AND tablename = 'syllabus'
                    );
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    print("🔨 Creating syllabus table...")
                    cur.execute("""
                        CREATE TABLE syllabus (
                            id SERIAL PRIMARY KEY,
                            course_code VARCHAR(50) UNIQUE NOT NULL,
                            course_name VARCHAR(255) NOT NULL,
                            department VARCHAR(100),
                            semester VARCHAR(20),
                            credits INTEGER,
                            syllabus_content TEXT
                        )
                    """)
                    print("✅ syllabus table created successfully!")
                else:
                    print("✅ syllabus table already exists.")
                
                # Add columns if they don't exist (for existing tables)
                try:
                    cur.execute("ALTER TABLE syllabus ADD COLUMN IF NOT EXISTS course_code VARCHAR(50);")
                    cur.execute("ALTER TABLE syllabus ADD COLUMN IF NOT EXISTS course_name VARCHAR(255);")
                    cur.execute("ALTER TABLE syllabus ADD COLUMN IF NOT EXISTS department VARCHAR(100);")
                    cur.execute("ALTER TABLE syllabus ADD COLUMN IF NOT EXISTS semester VARCHAR(20);")
                    cur.execute("ALTER TABLE syllabus ADD COLUMN IF NOT EXISTS credits INTEGER;")
                    cur.execute("ALTER TABLE syllabus ADD COLUMN IF NOT EXISTS syllabus_content TEXT;")
                    print("   - All columns verified")
                except Exception as e:
                    print(f"   ⚠️  Column check: {e}")
                
                # Create indexes for faster queries
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_course_code ON syllabus(course_code);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_department ON syllabus(department);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_semester ON syllabus(semester);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_course_name ON syllabus(course_name);")
                print("   - Indexes created")
                
                conn.commit()
                print("\n✅ Database setup complete!")
                
    except Exception as e:
        print(f"❌ Error creating/updating syllabus table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_syllabus_table()

