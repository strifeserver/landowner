
import sqlite3
import os

# Adjusted path for being inside 'test/' folder
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'data.db'))

def check_navigations():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    print(f"Checking DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Searching for CRUD related navigations ---")
    try:
        cursor.execute("SELECT id, menu_name, navigation, is_hidden, status FROM navigations WHERE menu_name LIKE '%Crud%' OR navigation LIKE '%crud%'")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"Found: {row}")
        else:
            print("No CRUD navigation found.")
            
        print("\n--- All Navigations ---")
        cursor.execute("SELECT id, menu_name, navigation_order FROM navigations ORDER BY navigation_order")
        rows = cursor.fetchall() # Need to fetch again
        for row in rows:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_navigations()
