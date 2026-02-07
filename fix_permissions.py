import sqlite3
import os

DB_PATH = os.path.join('data', 'data.db')

def update_permissions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current permissions for Administrator (ID 1)
    cursor.execute('SELECT "add", "edit", "delete" FROM access_levels WHERE id=1')
    row = cursor.fetchone()
    
    if not row:
        print("Administrator access level not found.")
        return

    add_perms = row[0].split(',') if row[0] else []
    edit_perms = row[1].split(',') if row[1] else []
    del_perms = row[2].split(',') if row[2] else []
    
    # Add navigation ID 9 (CRUD Builder) to permissions
    if '9' not in add_perms:
        add_perms.append('9')
    if '9' not in edit_perms:
        edit_perms.append('9')
    if '9' not in del_perms:
        del_perms.append('9')
        
    cursor.execute('UPDATE access_levels SET "add"=?, "edit"=?, "delete"=? WHERE id=1', 
                   (','.join(add_perms), ','.join(edit_perms), ','.join(del_perms)))
    
    conn.commit()
    conn.close()
    print("Successfully granted CRUD Builder permissions to Administrator.")

if __name__ == "__main__":
    update_permissions()
