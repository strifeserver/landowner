# table_buttons.py
from utils.form_popup import open_form_popup
from utils.debug import print_r

def on_add(table_view):
    field_definitions = table_view.trigger_controller_method("create")

    if not field_definitions:
        print("No form field definitions returned.")
        return

    def on_submit(data):
        print("Form submitted with data:", data)
        table_view.trigger_controller_method("store", data=data)

        # Refresh table
        table_view.original_data = table_view.controller_callback() or []
        table_view.filtered_data = table_view.original_data.copy()
        table_view.render_rows()
        
    open_form_popup("Insert Data", field_definitions, on_submit=on_submit)


def on_edit(table_view: "TableView"):
    selected = table_view.tree.selection()
    if not selected:
        return

    # Get first selected item
    item_id = selected[0]

    # Tkinter Treeview selection returns iid (not index)
    # To get the row object, we can use the index from filtered_data
    item_index = table_view.tree.index(item_id)
    row = table_view.filtered_data[item_index]

    # Now pass the full row object to your controller
    table_view.trigger_controller_method("edit", data=row)


    field_definitions = table_view.trigger_controller_method("create")  # reuse field metadata
    
    print('Table Buttons')
    print(' ')


    def on_submit(data):
     
        table_view.trigger_controller_method("update", id=row.id, data=data)

        # Refresh table
        table_view.original_data = table_view.controller_callback() or []
        table_view.filtered_data = table_view.original_data.copy()
        table_view.render_rows()

    open_form_popup("Update Data", field_definitions, on_submit=on_submit, initial_data=row)


def on_delete(table_view):
    selected = table_view.tree.selection()
    if not selected:
        return
    index = int(selected[0])
    row = table_view.filtered_data[index]
    row_id = row.get("id", None)
    if row_id is None:
        from tkinter import messagebox

        messagebox.showerror("Delete Error", "No 'id' field found in the selected row.")
        return
    from tkinter import messagebox

    if messagebox.askyesno("Confirm Delete", f"Delete item with ID: {row_id}?"):
        table_view.trigger_controller_method("destroy", id=row_id)
        table_view.original_data = [
            r for r in table_view.original_data if r.get("id") != row_id
        ]
        table_view.filtered_data = [
            r for r in table_view.filtered_data if r.get("id") != row_id
        ]
        table_view.render_rows()
