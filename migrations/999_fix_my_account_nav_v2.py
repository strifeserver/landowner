import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def fix_nav():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Revert Accounts Management (ID 2)
    print("Reverting Accounts Management...")
    cursor.execute("""
        UPDATE navigations 
        SET controller = NULL,
            navigation = NULL
        WHERE id = 2
    """)

    # Check if 'My Account' child menu exists under ID 2 or elsewhere
    cursor.execute("SELECT id FROM navigations WHERE menu_name = 'My Account'")
    row = cursor.fetchone()

    if row:
        print(f"Updating existing My Account (ID: {row[0]})...")
        cursor.execute("""
            UPDATE navigations 
            SET controller = 'MyAccountController',
                navigation = 'my_account'
            WHERE id = ?
        """, (row[0],))
    else:
        print("Adding My Account child menu under Accounts Management (ID 2)...")
        cursor.execute("""
            INSERT INTO navigations (menu_name, navigation, navigation_type, parent_id, controller, navigation_order, status, created_at, updated_at)
            VALUES ('My Account', 'my_account', 'child_menu', 2, 'MyAccountController', 1, 'active', DATETIME('now'), DATETIME('now'))
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_nav()
