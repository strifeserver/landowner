import sqlite3
import os
import json

DB_PATH = os.path.join("data", "data.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT settings_json FROM table_settings WHERE table_name='users'")
row = cursor.fetchone()
if row:
    print(json.dumps(json.loads(row[0]), indent=2))
else:
    print("None")

conn.close()
