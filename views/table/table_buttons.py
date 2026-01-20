# table_buttons.py
from utils.form_popup import open_form_popup
from utils.debug import print_r
from utils.safe_launcher import safe_launch
from utils.Alert import Alert

def on_add(table_view: "TableView"):
    # 1. NEW: Check for dynamic view selection from the controller's create method
    instruction = table_view.trigger_controller_method("create")

    if not instruction:
        print("No form instructions returned.")
        return

    # Handle legacy controllers that only return field_definitions
    if not isinstance(instruction, dict) or "view_type" not in instruction:
        field_definitions = instruction
        initial_data = None
        view_type = "generic"
        view_class = open_form_popup
    else:
        view_type = instruction.get("view_type", "generic")
        view_class = instruction.get("view_class", open_form_popup) if view_type == "custom" else open_form_popup
        field_definitions = instruction.get("field_definitions")
        initial_data = instruction.get("initial_data")

    def on_submit(data):
        print("Form submitted with data:", data)
        response = table_view.trigger_controller_method("store", data=data)

        if isinstance(response, dict):
            if response.get("success"):
                Alert.success(response.get("message"))
                # Re-fetch and re-render data from controller
                table_view.render_rows()
            elif "errors" in response:
                Alert.error(response["errors"], title="Validation Error")
            else:
                Alert.error(response.get("message"))
        
        return response

    if view_type == "custom" and view_class:
        safe_launch(view_class, table_view.winfo_toplevel(), callback=on_submit, **(initial_data or {}))
    else:
        safe_launch(open_form_popup, "Insert Data", field_definitions, on_submit=on_submit, initial_data=initial_data)


def on_edit(table_view: "TableView"):
    selected = table_view.tree.selection()
    if not selected:
        return

    # Get first selected item
    item_id = selected[0]
    item_index = table_view.tree.index(item_id)
    row = table_view.filtered_data[item_index]

    # 1. NEW: Check for dynamic view selection from the controller's edit method
    instruction = table_view.trigger_controller_method("edit", data=row)

    if not instruction:
        print("No edit instructions returned.")
        return

    # Handle legacy controllers that only return the row or None
    if not isinstance(instruction, dict) or "view_type" not in instruction:
        # Backward compatibility: use create() for definitions
        field_definitions = table_view.trigger_controller_method("create")
        initial_data = instruction if instruction is not None else row
        view_type = "generic"
        view_class = open_form_popup
    else:
        view_type = instruction.get("view_type", "generic")
        view_class = instruction.get("view_class", open_form_popup) if view_type == "custom" else open_form_popup
        field_definitions = instruction.get("field_definitions")
        initial_data = instruction.get("initial_data", row)

    def on_submit(data):
        response = table_view.trigger_controller_method("update", id=row.id, data=data)

        if isinstance(response, dict):
            if response.get("success"):
                Alert.success(response.get("message"))
                # Refresh table
                table_view.original_data = table_view.controller_callback() or []
                table_view.filtered_data = table_view.original_data.copy()
                table_view.render_rows()
            elif "errors" in response:
                Alert.error(response["errors"], title="Validation Error")
            else:
                Alert.error(response.get("message"))
            
        return response

    if view_type == "custom" and view_class:
        # For custom views, we assume they handle their own data loading via ID
        safe_launch(view_class, table_view.winfo_toplevel(), item_id=row.id, callback=on_submit)
    else:
        safe_launch(open_form_popup, "Update Data", field_definitions, on_submit=on_submit, initial_data=initial_data)


def on_delete(table_view: "TableView"):
    selected = table_view.tree.selection()
    if not selected:
        return
    
    # Correctly get the numerical index from the Treeview ID
    item_id = selected[0]
    index = table_view.tree.index(item_id)
    row = table_view.filtered_data[index]
    
    # Robustly get the ID whether row is a dict or object
    row_id = getattr(row, "id", None) if not isinstance(row, dict) else row.get("id")
    
    if row_id is None:
        Alert.error("No 'id' field found in the selected row.", title="Delete Error")
        return
    def execute_delete():
        response = table_view.trigger_controller_method("destroy", id=row_id)
        
        if isinstance(response, dict) and response.get("success"):
            Alert.success(response.get("message", "Deleted successfully"))
            # Reset to page 1 and refresh
            table_view.current_page = 1
            table_view.render_rows()
        else:
            msg = response.get("message", "Delete failed") if isinstance(response, dict) else "Delete failed"
            Alert.error(msg)

    Alert.confirm(
        f"Delete item with ID: {row_id}?",
        title="Confirm Delete",
        on_confirm=execute_delete
    )
