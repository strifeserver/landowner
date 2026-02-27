# test_security_improvements.py
"""
Verification script for password hashing and memory optimization.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "data.db")

def check_password_hashing():
    """Verify that passwords in the database are hashed."""
    print("=" * 60)
    print("CHECKING PASSWORD HASHING")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password FROM users LIMIT 5")
    users = cursor.fetchall()
    
    for user_id, username, password in users:
        is_hashed = password and (password.startswith('$2b$') or password.startswith('$2a$'))
        status = "✓ HASHED" if is_hashed else "✗ PLAINTEXT"
        print(f"User {user_id} ({username}): {status}")
        if is_hashed:
            print(f"  Hash preview: {password[:29]}...")
    
    conn.close()
    print()

def check_audit_fields():
    """Verify audit fields are populated."""
    print("=" * 60)
    print("CHECKING AUDIT FIELDS")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, created_by, updated_by, created_at, updated_at 
        FROM users 
        WHERE created_by IS NOT NULL 
        LIMIT 3
    """)
    users = cursor.fetchall()
    
    for user_id, username, created_by, updated_by, created_at, updated_at in users:
        print(f"User {user_id} ({username}):")
        print(f"  Created by: {created_by} at {created_at}")
        print(f"  Updated by: {updated_by} at {updated_at}")
    
    conn.close()
    print()

if __name__ == "__main__":
    check_password_hashing()
    check_audit_fields()
    
    print("=" * 60)
    print("MANUAL VERIFICATION REQUIRED:")
    print("=" * 60)
    print("1. Login with existing user (test auto-migration)")
    print("2. Create new user and verify bcrypt hash in DB")
    print("3. Change user photo multiple times")
    print("4. Monitor memory usage in footer (should stabilize)")
    print("5. Verify created_by/updated_by NOT shown in forms")
