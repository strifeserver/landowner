# table_buttons.py
from utils.form_popup import open_form_popup


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


def on_edit(table_view):
    print('ON EDIT')
    print(table_view)
    selected = table_view.tree.selection()
    if not selected:
        return
    index = int(selected[0])
    row = table_view.filtered_data[index]
    row_id = row.get("id")



    field_definitions = table_view.trigger_controller_method("create")  # reuse field metadata
    
    print('FIELD DEFINITIONS')
    print(table_view.trigger_controller_method("create"))
    

    def on_submit(data):
        table_view.trigger_controller_method("update", id=row_id, data=data)

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
