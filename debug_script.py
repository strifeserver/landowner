import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from models.CrudBuilder import CrudBuilder
from services.CrudBuilderService import CrudBuilderService
import json

def test():
    try:
        from models.base_model import BaseModel
        # Patch BaseModel.store_sqlite to see if it's even hit
        original_store = BaseModel.store_sqlite
        def patched_store(cls, db_path, table_name, **kwargs):
            print(f"Patched store hit! table_name={table_name}")
            return original_store(db_path, table_name, **kwargs)
        BaseModel.store_sqlite = classmethod(patched_store)

        s = CrudBuilderService()
        data = {'name': 'Payments', 'fields_json': '[]'}
        print("Starting generate_module...")
        s.generate_module(data)
        print("Done")
    except KeyError as e:
        print(f"KeyError caught: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"Exception caught: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
