from models.table_setting import TableSetting
import json

def verify_access_levels():
    print("Checking Table Settings for 'access_levels'...")
    setting = TableSetting.fetch_by_table_name("access_levels")
    
    if not setting:
        print("ERROR: No setting found for 'access_levels'")
        return

    print(f"Setting Found: ID={setting.id}")
    print(f"Items Per Page: {setting.items_per_page}")
    print(f"Table Height: {setting.table_height}")
    
    if not setting.settings_json:
        print("Settings JSON is empty/None")
        return

    try:
        data = json.loads(setting.settings_json)
        print(f"Settings JSON parsed successfully. Count: {len(data)}")
        for col in data:
            print(f"  - {col.get('name')}: Visible={col.get('visible')}, Order={col.get('order')}, Alias='{col.get('alias')}'")
    except Exception as e:
        print(f"ERROR parsing JSON: {e}")

if __name__ == "__main__":
    verify_access_levels()
