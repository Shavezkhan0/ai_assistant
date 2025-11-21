"""Delete all syllabus entries from the database"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def delete_all_syllabus():
    conn_string = os.getenv('POSTGRES_CONNECTION_STRING')
    if not conn_string:
        print("❌ POSTGRES_CONNECTION_STRING not found in .env")
        return
    
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Count existing entries
                cur.execute("SELECT COUNT(*) FROM syllabus")
                count = cur.fetchone()[0]
                
                if count == 0:
                    print("✅ No syllabus entries found. Database is already empty.")
                    return
                
                print(f"📋 Found {count} syllabus entries")
                
                # Delete all entries
                print("🗑️  Deleting all syllabus entries...")
                cur.execute("DELETE FROM syllabus")
                
                # Verify deletion
                cur.execute("SELECT COUNT(*) FROM syllabus")
                remaining = cur.fetchone()[0]
                
                conn.commit()
                
                if remaining == 0:
                    print(f"✅ Successfully deleted {count} syllabus entries!")
                    print("   Database is now empty. You can reupload syllabus PDFs.")
                else:
                    print(f"⚠️  Warning: {remaining} entries still remain.")
                
    except Exception as e:
        print(f"❌ Error deleting syllabus: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    delete_all_syllabus()
