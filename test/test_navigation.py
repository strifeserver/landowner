import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.navigation import Navigation  # only once

def test_index():


    # No filter - return all
    navigationAll = Navigation.index()
    # navigationAll = Navigation.index(search="dash")
    print('navigation ALL:')
    print(navigationAll)

    # # Filter specific field
    # userFilterSpecific = User.index(filters={"username": "jean"})
    # print('User filter specific field')
    # print(userFilterSpecific)

    # # Global search on all fields
    # userFilterAll = User.index(search="jean")
    # print('user filter all field')
    # print(userFilterAll)

    # # Combination: filter and pagination
    # print("Filtered by username='jean' with pagination (page 1)")
    # filtered_paginated = User.index(filters={"username": "jean"}, pagination=True, items_per_page=5, page=1)
    # print(filtered_paginated)

    # print("Search='jean' with pagination (page 1)")
    # search_paginated = User.index(search="jean", pagination=True, items_per_page=5, page=1)
    # print(search_paginated)



if __name__ == "__main__":
    test_index()
