# test/test_crud_builder_service.py
import os
import sys
import json
import sqlite3

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.CrudBuilderService import CrudBuilderService

def test_generate_payments():
    service = CrudBuilderService()
    
    fields = [
        {"alias": "Expense Name", "name": "expense_name", "type": "text", "visible": True, "editable": True},
        {"alias": "Cost", "name": "cost", "type": "number", "visible": True, "editable": True},
        {"alias": "Order Number", "name": "order_number", "type": "text", "visible": True, "editable": True}
    ]
    
    data = {
        "name": "Payments",
        "fields_json": json.dumps(fields),
        "sort_field": "id",
        "sort_direction": "DESC"
    }
    
    print("Testing generate_module for 'Payments'...")
    result = service.generate_module(data)
    print("Result:", result)
    
    if result.get("success"):
        print("Verification steps:")
        print(f"- Check models/Payments.py: {os.path.exists('models/Payments.py')}")
        print(f"- Check services/PaymentsService.py: {os.path.exists('services/PaymentsService.py')}")
        print(f"- Check controllers/PaymentsController.py: {os.path.exists('controllers/PaymentsController.py')}")
        
        # Check DB
        DB_PATH = os.path.join("data", "data.db")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM navigations WHERE menu_name = 'Payments'")
        nav = cursor.fetchone()
        print(f"- Check navigation entry: {nav is not None}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
        tbl = cursor.fetchone()
        print(f"- Check payments table: {tbl is not None}")
        
        conn.close()
    else:
        print("FAILED to generate module")

if __name__ == "__main__":
    test_generate_payments()
