# utils/form_popup.py
import tkinter as tk
from tkinter import ttk
from utils.Alert import Alert

def open_form_popup(title, field_definitions, on_submit, initial_data=None):
    """
    Opens a generic form popup for creating or editing a record.
    Dynamically switches to 2-column layout if there are many fields.
    """
    popup = tk.Toplevel()
    popup.title(title)
    
    entries = {}
    
    # Filter visible fields first to determine layout
    visible_fields = []
    for field_name, config in field_definitions.items():
        if field_name in ("id", "created_at", "updated_at"):
            continue
        if config.get("is_hidden") is True:
            continue
        visible_fields.append((field_name, config))
    
    field_count = len(visible_fields)
    use_two_columns = field_count > 6
    
    # Calculate initial geometry estimate
    if use_two_columns:
        popup.geometry("800x600") # Two columns, wider
    else:
        popup.geometry("400x500") # Single column

    # Main container (holds Fields + Button Frame)
    main_container = tk.Frame(popup, padx=20, pady=20)
    main_container.pack(fill="both", expand=True)

    # 1. Fields Container (Grid)
    fields_frame = tk.Frame(main_container)
    fields_frame.pack(fill="both", expand=True, side="top")

    # Grid configuration for fields_frame
    if use_two_columns:
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
    else:
        fields_frame.columnconfigure(0, weight=1)

    for i, (field_name, config) in enumerate(visible_fields):
        # ... logic ...
        label = config.get("alias", field_name)
        is_editable = config.get("editable", True)
        options = config.get("options", None)

        if isinstance(initial_data, dict):
            value = initial_data.get(field_name, "")
        elif initial_data is not None:
            value = getattr(initial_data, field_name, "")
        else:
            value = ""
        if value is None:
            value = ""

        if use_two_columns:
            row = i // 2
            col = i % 2
            padx = (0, 10) if col == 0 else (10, 0)
        else:
            row = i
            col = 0
            padx = 0

        # Field Frame (Cell)
        frame = tk.Frame(fields_frame)
        frame.grid(row=row, column=col, sticky="new", padx=padx, pady=5)
        
        tk.Label(frame, text=label, anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X)

        if options is not None:
            input_widget = create_dropdown_field(frame, options, value, is_editable)
        else:
            input_widget = create_text_field(frame, value, is_editable)

        entries[field_name] = input_widget

    # 2. Button Container (Bottom)
    btn_frame = tk.Frame(main_container, pady=20)
    btn_frame.pack(fill="x", side="bottom")

    submit_btn = tk.Button(
        btn_frame, 
        text="Submit", 
        width=20, # Fixed width
        command=lambda: handle_submit(entries, on_submit, popup),
        height=2
    )
    submit_btn.pack() # Center by default


def create_text_field(parent, value="", editable=True):
    entry = tk.Entry(parent)
    entry.insert(0, str(value))
    if not editable:
        entry.config(state="disabled")
    entry.pack(fill=tk.X, ipady=3)
    return entry


def create_dropdown_field(parent, options, current_value=None, editable=True):
    """
    Creates a Combobox.
    Returns a tuple: (StringVar, label_to_value_map)
    """
    # Check if options are objects with label/value
    # Robust check: allow empty options to treat as object list if needed, or simple list
    # But usually empty options means nothing to select.
    
    is_object_list = False
    if options and isinstance(options, list):
        if len(options) > 0 and isinstance(options[0], dict) and "label" in options[0] and "value" in options[0]:
            is_object_list = True
    
    # Handle empty options case for object list logic (if field definition implies it)
    # Here we infer from first item. If empty, default to simple string list (doesn't matter much)

    combo_values = []
    label_to_value = {}
    value_to_label = {}
    
    if is_object_list:
        for opt in options:
            lbl = str(opt["label"])
            val = opt["value"]
            label_to_value[lbl] = val
            value_to_label[str(val)] = lbl # Key by string representation of value
            combo_values.append(lbl)
            
        # Determine default selected label from current_value
        default_label = value_to_label.get(str(current_value), "")
        if not default_label and current_value == "": 
             # If current value is empty and no label matches, try to pick first or leave empty
             default_label = ""
        elif not default_label:
             # If value has no label, show value as label?
             default_label = str(current_value)

    else:
        # Simple list
        combo_values = [str(x) for x in options]
        default_label = str(current_value)
        # Verify if value matches one of the options, otherwise might want to default to ""?
        # Combobox can hold custom text though.

    var = tk.StringVar(value=default_label)

    combobox = ttk.Combobox(
        parent,
        textvariable=var,
        values=combo_values,
        state="readonly" if not editable else "normal",
    )
    combobox.pack(fill=tk.X, ipady=3)

    return (var, label_to_value)


def handle_submit(entries, on_submit, popup):
    data = {}
    for field, widget in entries.items():
        if isinstance(widget, tk.Entry):
            data[field] = widget.get()
        elif isinstance(widget, tuple):
            # It is a dropdown (var, label_to_value)
            var, label_to_value = widget
            selected_label = var.get()
            
            if label_to_value and selected_label in label_to_value:
                # Ensure we strictly mapped back to the value expected by the database/model
                data[field] = label_to_value[selected_label]
            else:
                # Fallback: maybe the value itself is selected or it's a direct entry
                # Check if the selected label IS a key in our value map (case sensitivity?)
                # For now, just use what we have, but validation might fail if it expects "menu" and gets "Menu"
                # If label_to_value exists, we should try to find the value
                found = False
                if label_to_value:
                    for lbl, val in label_to_value.items():
                        if lbl == selected_label:
                             data[field] = val
                             found = True
                             break
                if not found:
                    data[field] = selected_label
        else:
            data[field] = None

    if callable(on_submit):
        response = on_submit(data)
        
        if isinstance(response, dict):
            if response.get("success"):
                popup.destroy()
        else:
            popup.destroy()
