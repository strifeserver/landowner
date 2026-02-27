
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.db")

def migrate():
    print("Migrating: Adding Crud Builder Navigation...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Check if it already exists (just in case)
        cursor.execute("SELECT id FROM navigations WHERE navigation = 'crud_builder'")
        existing = cursor.fetchone()
        
        crud_nav_id = None
        
        if existing:
            print("Crud Builder navigation already exists. Updating...")
            crud_nav_id = existing[0]
            cursor.execute("""
                UPDATE navigations 
                SET menu_name = 'Crud Builder', 
                    controller = 'CrudBuilderController', 
                    is_hidden = 0, 
                    status = 'active',
                    navigation_order = 95
                WHERE id = ?
            """, (crud_nav_id,))
        else:
            print("Creating Crud Builder navigation...")
            cursor.execute("""
                INSERT INTO navigations (
                    menu_name, navigation, navigation_order, navigation_type,
                    parent_id, controller, is_hidden, status, created_at, updated_at
                ) VALUES (
                    'Crud Builder', 'crud_builder', 95, 'menu', 
                    NULL, 'CrudBuilderController', 0, 'active', 
                    DATETIME('now'), DATETIME('now')
                )
            """)
            crud_nav_id = cursor.lastrowid
            
        print(f"Crud Builder Navigation ID: {crud_nav_id}")

        # 2. Add permissions to Admin
        # Find Admin role
        cursor.execute("SELECT id, view, 'add', edit, 'delete' FROM access_levels WHERE access_level_code = 'admin'") # access_level_code might be 'admin'
        # Note: Previous migrations suggest looking up by name or code. Let's try code first.
        # But wait, 'add', 'delete' are reserved words in SQL maybe? I should quote them.
        # Actually in Python string it's fine.
        
        # Let's just select *
        cursor.execute("SELECT * FROM access_levels WHERE access_level_code = 'admin'")
        admin_role = cursor.fetchone()
        
        if not admin_role:
             # Try name
            cursor.execute("SELECT * FROM access_levels WHERE access_level_name = 'Admin'")
            admin_role = cursor.fetchone()
            
        if admin_role:
            print(f"Updating Admin permissions for ID {admin_role[0]}...")
            
            # Helper to append ID to CSV
            def append_id(current_val, new_id):
                if not current_val:
                    return str(new_id)
                ids = [x.strip() for x in str(current_val).split(',') if x.strip()]
                if str(new_id) not in ids:
                    ids.append(str(new_id))
                return ",".join(ids)

            # Columns in access_levels table: id, name, code, ... view, add, edit, delete, export, import ...
            # I need to know the column indices or just update by name.
            # It's safer to read headers or just fetch specific columns.
            # Let's assume standard columns: view, add, edit, delete
            
            cursor.execute("SELECT view, `add`, edit, `delete` FROM access_levels WHERE id = ?", (admin_role[0],))
            perms = cursor.fetchone()
            
            new_view = append_id(perms[0], crud_nav_id)
            new_add = append_id(perms[1], crud_nav_id)
            new_edit = append_id(perms[2], crud_nav_id)
            new_delete = append_id(perms[3], crud_nav_id)
            
            cursor.execute("""
                UPDATE access_levels 
                SET view = ?, `add` = ?, edit = ?, `delete` = ?
                WHERE id = ?
            """, (new_view, new_add, new_edit, new_delete, admin_role[0]))
            
            print("Admin permissions updated.")
        else:
            print("Admin role not found. Skipping permission update.")

        conn.commit()
        print("Migration complete.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
