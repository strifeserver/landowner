import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Adding 'google_sheet_last_login_validate_days' setting...")
    
    try:
        # Check if setting already exists
        cursor.execute("SELECT COUNT(*) FROM settings WHERE setting_name = 'google_sheet_last_login_validate_days'")
        exists = cursor.fetchone()[0]
        
        if not exists:
            cursor.execute("""
                INSERT INTO settings (setting_name, setting_value, created_at, updated_at)
                VALUES ('google_sheet_last_login_validate_days', '7', datetime('now'), datetime('now'))
            """)
            print("Setting 'google_sheet_last_login_validate_days' added with default value: 7")
        else:
            print("Setting 'google_sheet_last_login_validate_days' already exists.")
    except Exception as e:
        print(f"Error adding setting: {e}")

    conn.commit()
    conn.close()
    print("Migration 011_add_sheet_validation_setting complete.")

if __name__ == "__main__":
    migrate()
