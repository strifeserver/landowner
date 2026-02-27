import tkinter as tk
from views.main_window import MainWindow
from utils.session import Session
from models.user import User
from models.access_level import AccessLevel
from models.navigation import Navigation

def test_nav_permissions():
    print("--- 1. Testing Admin View (Access Level 1) ---")
    # Simulate Login Admin
    users = User.index(filters={"username": "admin"})
    if not users:
        print("FAIL: Admin user not found.")
        return
    admin = users[0]
    Session.set_user(admin)
    print(f"Logged in as: {admin.username} (Access Level: {admin.access_level})")

    # Mock MainWindow logic because we don't want to spawn GUI
    # We just run the logic inside load_navigation adapted for script
    
    # Logic from MainWindow.load_navigation
    all_menu_items = Navigation.index()
    access_level = AccessLevel.edit(admin.access_level)
    allowed_ids = access_level.get_permissions_list('view')
    print(f"Allowed IDs: {allowed_ids}")
    
    filtered_items = [item for item in all_menu_items if item.id in allowed_ids]
    print(f"Items Visible: {[item.menu_name for item in filtered_items]}")
    
    if len(filtered_items) >= 4: # Assuming seed has 4 items
        print("PASS: Admin sees all items.")
    else:
        print(f"FAIL: Admin missing items. Expected >=4, got {len(filtered_items)}")

    print("\n--- 2. Testing Tenant View (Access Level 3) ---")
    # Simulate Tenant
    # If no tenant user exists, create one temporarily or mock logic
    users = User.index(filters={"access_level": 3})
    if not users:
        print("Creating temp tenant...")
        # Just mock the ID lookup
        class MockUser:
            access_level = 3
            username = "mock_tenant"
        tenant = MockUser()
    else:
        tenant = users[0]

    Session.set_user(tenant)
    print(f"Logged in as: {tenant.username} (Access Level: {tenant.access_level})")
    
    access_level = AccessLevel.edit(tenant.access_level) # Should return Tenant role
    if not access_level:
        print("FAIL: Access Level 3 not found in DB!")
        return
        
    print(f"Raw View Data for ID 3: '{access_level.view}'")
    allowed_ids = access_level.get_permissions_list('view')
    print(f"Allowed IDs: {allowed_ids}")
    
    filtered_items = [item for item in all_menu_items if item.id in allowed_ids]
    print(f"Items Visible: {[item.menu_name for item in filtered_items]}")
    
    if len(filtered_items) == 0:
        print("PASS: Tenant sees 0 items.")
    else:
        print(f"FAIL: Tenant sees items! Expected 0, got {len(filtered_items)}")

if __name__ == "__main__":
    try:
        test_nav_permissions()
    except Exception as e:
        print(f"CRASH: {e}")
