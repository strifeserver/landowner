import sqlite3
import os
import json

DB_PATH = os.path.join(os.getcwd(), 'data', 'data.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all table settings
cursor.execute("SELECT id, table_name, settings_json FROM table_settings")
settings = cursor.fetchall()

print("=== TABLE SETTINGS IN DATABASE ===")
for s in settings:
    print(f"\nID: {s[0]} | Table: {s[1]}")
    if s[2]:
        try:
            parsed = json.loads(s[2])
            print(f"Settings JSON:")
            for col in parsed:
                visible = col.get('visible', True)
                print(f"  - {col.get('name')}: visible={visible}, order={col.get('order')}")
        except:
            print(f"  Raw JSON: {s[2]}")
    else:
        print("  No settings_json")

conn.close()
