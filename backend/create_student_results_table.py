"""Create student_results table in PostgreSQL"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def create_student_results_table():
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
                        AND tablename = 'student_results'
                    );
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    print("🔨 Creating student_results table...")
                    cur.execute("""
                        CREATE TABLE student_results (
                            id SERIAL PRIMARY KEY,
                            student_id VARCHAR(50) NOT NULL,
                            student_name VARCHAR(255),
                            programme VARCHAR(255),
                            branch VARCHAR(255),
                            institute VARCHAR(500),
                            subject VARCHAR(255) NOT NULL,
                            marks FLOAT,
                            grade VARCHAR(10),
                            semester VARCHAR(20),
                            paper_id VARCHAR(20),
                            internal_marks FLOAT,
                            external_marks FLOAT,
                            credits INTEGER
                        )
                    """)
                    print("✅ student_results table created successfully!")
                else:
                    print("✅ student_results table already exists.")
                
                # Add columns if they don't exist (for existing tables)
                try:
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS programme VARCHAR(255);")
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS branch VARCHAR(255);")
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS institute VARCHAR(500);")
                    # Add new columns for paper_id, internal_marks, external_marks, credits
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS paper_id VARCHAR(20);")
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS internal_marks FLOAT;")
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS external_marks FLOAT;")
                    cur.execute("ALTER TABLE student_results ADD COLUMN IF NOT EXISTS credits INTEGER;")
                    print("   - All columns verified (including paper_id, internal_marks, external_marks, credits)")
                except Exception as e:
                    print(f"   ⚠️  Column check: {e}")
                
                # Create indexes for faster queries
                cur.execute("CREATE INDEX IF NOT EXISTS idx_student_id ON student_results(student_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_student_semester ON student_results(student_id, semester);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_student_name ON student_results(student_name);")
                print("   - Indexes created")
                
                conn.commit()
                print("\n✅ Database setup complete!")
                
    except Exception as e:
        print(f"❌ Error creating/updating student_results table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_student_results_table()

