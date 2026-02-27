import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

# Set last_login to 8 days ago
eight_days_ago = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
cursor.execute('UPDATE users SET last_login = ? WHERE username = ?', (eight_days_ago, 'merchant'))
conn.commit()

# Verify
cursor.execute('SELECT username, last_login, spreadsheet_validation FROM users WHERE username = ?', ('merchant',))
result = cursor.fetchone()

print(f'Updated merchant user:')
print(f'  Username: {result[0]}')
print(f'  Last Login: {result[1]}')
print(f'  Spreadsheet Validation: {"Enabled" if result[2] else "Disabled"}')

conn.close()
