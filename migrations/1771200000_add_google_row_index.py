import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_update = ['orders', 'order_items', 'payments', 'expenses', 'users']
    
    for table in tables_to_update:
        try:
            # Check if column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'google_row_index' not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN google_row_index INTEGER")
                print(f"Added google_row_index to {table}")
            else:
                print(f"google_row_index already exists in {table}")
                
        except Exception as e:
            print(f"Error updating {table}: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
