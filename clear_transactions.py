import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'data.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    print("Clearing transaction data...")
    
    tables = ['order_items', 'expenses', 'payments', 'orders']
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"✓ Cleared table: {table}")
        
    # Reset auto-increment counters
    for table in tables:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        print(f"✓ Reset auto-increment for: {table}")
    
    conn.commit()
    print("\n✅ All transaction data cleared successfully!")
    
except Exception as e:
    print(f"\n❌ Error clearing data: {e}")
    conn.rollback()
finally:
    conn.close()
