import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def update_nav():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find My Account
    cursor.execute("SELECT id, menu_name FROM navigations WHERE menu_name LIKE '%Account%'")
    rows = cursor.fetchall()
    print(f"Found navigation rows: {rows}")

    if rows:
        for row_id, name in rows:
            print(f"Updating {name} (ID: {row_id}) to MyAccountController...")
            cursor.execute("""
                UPDATE navigations 
                SET controller = 'MyAccountController',
                    navigation = 'my_account'
                WHERE id = ?
            """, (row_id,))
    else:
        print("My Account navigation not found. Adding it...")
        # Add it if missing
        cursor.execute("""
            INSERT INTO navigations (menu_name, navigation, navigation_type, controller, navigation_order, status, created_at, updated_at)
            VALUES ('My Account', 'my_account', 'menu', 'MyAccountController', 90, 'active', DATETIME('now'), DATETIME('now'))
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_nav()
