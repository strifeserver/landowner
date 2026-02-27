import sys
from models.user import User

print(f"Testing User.get_next_custom_id()...")
try:
    next_id = User.get_next_custom_id()
    print(f"Result: '{next_id}' (Type: {type(next_id)})")
except Exception as e:
    print(f"Error: {e}")
