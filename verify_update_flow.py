import os
import sys
import sqlite3
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.OrdersService import OrdersService
from models.user import User
from utils.session import Session
from models.Orders import Orders

def test_update_bundle():
    # 1. Setup session
    admin = User.index(filters={"username": "admin"})[0]
    Session.current_user = admin
    
    service = OrdersService()
    
    # Ensure at least one order exists
    orders = service.index(pagination=False)
    if not orders:
        print("Creating a temporary order for testing...")
        merchant = service.get_merchant_for_current_user()
        if not merchant:
            print("No merchant found, skipping test.")
            return
            
        bundle = {
            "order": {"customer_name": "Initial Customer", "customer_location": "Initial Location"},
            "items": [{"item_name": "Initial Item", "quantity": 1, "price": 100.0}]
        }
        res = service.store_order_bundle(bundle)
        order_id = res["order_id"]
    else:
        # Check if orders is a dict (pagination) or list
        if isinstance(orders, dict):
            order_id = orders["data"][0].id
        else:
            order_id = orders[0].id
            
    print(f"Testing Update for Order ID: {order_id}")
    
    # 3. Test Fetch Bundle
    bundle = service.get_order_bundle(order_id)
    print(f"Loaded Bundle: Order={bundle['order'].order_number}, Items={len(bundle['items'])}, Notes={len(bundle['notes'])}, Payments={len(bundle['payments'])}")

    # 4. Test Update Bundle
    update_data = {
        "order": {
            "customer_name": bundle['order'].customer_name + " (Updated)",
            "customer_location": "New Location"
        },
        "items": [
           {"item_name": "Updated Item 1", "quantity": 2, "price": 150.0}
        ],
        "new_note": "Verification update note executed.",
        "payment": {
            "amount_paid": 50.0,
            "payment_reference": "VERIFY-001",
            "payment_status": "partial"
        }
    }
    
    print("Executing update...")
    res = service.update_order_bundle(order_id, update_data)
    
    if res["success"]:
        print("Update successful!")
        new_bundle = service.get_order_bundle(order_id)
        print(f"Final State: Customer={new_bundle['order'].customer_name}, Location={new_bundle['order'].customer_location}")
        print(f"New Items Count: {len(new_bundle['items'])}")
        print(f"New Notes Count: {len(new_bundle['notes'])}")
        print(f"New Payments Count: {len(new_bundle['payments'])}")
        
        # Cleanup test data if created
        # conn = sqlite3.connect(os.path.join(project_root, 'data', 'data.db'))
        # ...
    else:
        print(f"Update failed: {res.get('message')}")

if __name__ == "__main__":
    test_update_bundle()
