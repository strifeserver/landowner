import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Ensuring 'spreadsheet_sync' columns exist in all required tables...")
    
    tables_to_update = [
        "orders",
        "order_items", 
        "payments",
        "expenses",
        "merchants"
    ]
    
    for table in tables_to_update:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN spreadsheet_sync INTEGER DEFAULT 0")
            print(f"✓ Column 'spreadsheet_sync' added to {table} table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"✓ Column 'spreadsheet_sync' already exists in {table} table.")
            else:
                print(f"✗ Error adding 'spreadsheet_sync' to {table}: {e}")

    conn.commit()
    conn.close()
    print("Migration 012_ensure_spreadsheet_sync complete.")

if __name__ == "__main__":
    migrate()
