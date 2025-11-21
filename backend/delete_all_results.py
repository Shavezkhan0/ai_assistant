"""Delete all student results from database"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def delete_all_results():
    conn_string = os.getenv('POSTGRES_CONNECTION_STRING')
    if not conn_string:
        print("❌ POSTGRES_CONNECTION_STRING not found")
        return
    
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Count records first
                cur.execute("SELECT COUNT(*) FROM student_results")
                count = cur.fetchone()[0]
                print(f"📊 Found {count} result records")
                
                if count == 0:
                    print("✅ Database is already empty")
                    return
                
                # Delete all records
                print("🗑️  Deleting all results...")
                cur.execute("DELETE FROM student_results")
                conn.commit()
                
                # Verify deletion
                cur.execute("SELECT COUNT(*) FROM student_results")
                remaining = cur.fetchone()[0]
                
                if remaining == 0:
                    print(f"✅ Successfully deleted {count} result records")
                else:
                    print(f"⚠️  Warning: {remaining} records still remain")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    confirm = input("⚠️  Are you sure you want to delete ALL results? (yes/no): ")
    if confirm.lower() == 'yes':
        delete_all_results()
    else:
        print("❌ Deletion cancelled")

