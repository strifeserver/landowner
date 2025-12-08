import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User  # only once
from requests.UserRequest import UserRequest
def test_index():


    # No filter - return all
    # userAll = User.index()
    # print('User ALL:')
    # print(userAll)

    # # Filter specific field
    # userFilterSpecific = User.index(filters={"username": "jean"})
    # print('User filter specific field')
    # print(userFilterSpecific)

    # # Global search on all fields
    # userFilterAll = User.index(search="jean")
    # print('user filter all field')
    # print(userFilterAll)
    # return
    # # Combination: filter and pagination
    # print("Filtered by username='jean' with pagination (page 1)")
    filtered_paginated = User.index(filters={"id": 1}, pagination=True, items_per_page=5, page=1)
    print(filtered_paginated)
    return

    # print("Search='jean' with pagination (page 1)")
    # search_paginated = User.index(search="jean", pagination=True, items_per_page=5, page=1)
    # print(search_paginated)

def test_store():
    new_user_data = {
        "username": "admin1",
        "password": "1234"
    }

    # 1. Create the request validator instance with data
    request = UserRequest(new_user_data)

    # 2. Run validation
    errors = request.validate()

    # 3. Check for errors
    # if errors:
    print("Validation errors:")
    print(errors)
    # print(request)
    return

    # # 4. If no errors, create the user
    # new_user = User.store(**new_user_data)
    # print("New user stored:")
    # print(vars(new_user))

if __name__ == "__main__":
    test_index()
