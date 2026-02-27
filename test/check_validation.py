import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'data.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT id, shop_name, is_sheet_validated FROM merchants")
merchants = cursor.fetchall()
for m in merchants:
    print(f"ID: {m[0]} | Shop: {m[1]} | Validated: {m[2]}")
conn.close()
