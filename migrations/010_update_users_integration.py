import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Adding 'spreadsheet_validation' and 'last_login' columns to users table...")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN spreadsheet_validation INTEGER DEFAULT 0")
        print("Column 'spreadsheet_validation' added.")
    except sqlite3.OperationalError:
        print("Column 'spreadsheet_validation' already exists.")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
        print("Column 'last_login' added.")
    except sqlite3.OperationalError:
        print("Column 'last_login' already exists.")

    conn.commit()
    conn.close()
    print("Migration 010_update_users_integration complete.")

if __name__ == "__main__":
    migrate()
