import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.CrudBuilderService import CrudBuilderService
from models.CrudBuilder import CrudBuilder

def run_regeneration():
    service = CrudBuilderService()
    
    # Modules to regenerate
    target_tables = ["orders", "merchants", "order_items"]
    
    # Get all CRUD definitions
    definitions = CrudBuilder.index()
    
    for definition in definitions:
        if definition.table_name in target_tables:
            print(f"Regenerating module: {definition.name} ({definition.table_name})...")
            
            data = {
                "name": definition.name,
                "fields_json": definition.fields_json,
                "sort_field": definition.sort_field,
                "sort_direction": definition.sort_direction
            }
            
            result = service.update_module(definition.id, data)
            if result.get("success"):
                print(f"Successfully regenerated {definition.name} and initialized table settings.")
            else:
                print(f"Failed to regenerate {definition.name}: {result.get('message')}")

if __name__ == "__main__":
    run_regeneration()
