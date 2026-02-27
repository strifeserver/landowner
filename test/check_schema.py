import sqlite3
import os

DB_PATH = 'data/data.db'
tables_to_check = ['orders', 'order_items', 'payments', 'expenses']
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for table_name in tables_to_check:
        print(f"Table: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = cursor.fetchall()
        for col in cols:
            if col[1] == 'spreadsheet_sync':
                # col[1] = name, col[2] = type, col[3] = notnull, col[4] = dflt_value, col[5] = pk
                print(f"  {col[1]} ({col[2]}) Default: {col[4]}")
    conn.close()
else:
    print(f"Database not found at {DB_PATH}")
