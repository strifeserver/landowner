import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Adding 'name' and 'display_photo' columns to users table...")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
    except sqlite3.OperationalError:
        print("Column 'name' already exists.")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN display_photo TEXT")
    except sqlite3.OperationalError:
        print("Column 'display_photo' already exists.")

    conn.commit()
    conn.close()
    print("Migration 007_update_users_table complete.")

if __name__ == "__main__":
    migrate()
