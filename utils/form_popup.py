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
        if field_name in ("id", "created_at", "updated_at", "created_by", "updated_by", "created_by_name", "updated_by_name"):
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
            field_type = config.get("type", "select")
            if field_type == "searchable_select":
                input_widget = create_searchable_dropdown(frame, options, value, is_editable)
            elif field_type == "multi_select":
                input_widget = create_multi_select(frame, options, value, is_editable)
            else:
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


def create_searchable_dropdown(parent, options, current_value=None, editable=True):
    """
    Creates a Combobox that filters its values based on user typing.
    Returns a tuple: (StringVar, label_to_value_map)
    """
    is_object_list = False
    if options and isinstance(options, list):
        if len(options) > 0 and isinstance(options[0], dict) and "label" in options[0] and "value" in options[0]:
            is_object_list = True

    combo_values = []
    label_to_value = {}
    value_to_label = {}
    
    if is_object_list:
        for opt in options:
            lbl = str(opt["label"])
            val = opt["value"]
            label_to_value[lbl] = val
            value_to_label[str(val)] = lbl
            combo_values.append(lbl)
            
        default_label = value_to_label.get(str(current_value), "")
        if not default_label and current_value == "": 
             default_label = ""
        elif not default_label:
             default_label = str(current_value)
    else:
        combo_values = [str(x) for x in options]
        default_label = str(current_value)

    var = tk.StringVar(value=default_label)

    # Use a standard Combobox but add filtering logic
    combobox = ttk.Combobox(
        parent,
        textvariable=var,
        values=combo_values,
        state="normal" if editable else "disabled" # Must be normal to type
    )
    combobox.pack(fill=tk.X, ipady=3)

    if not editable:
        return (var, label_to_value)

    # Store full list for filtering
    combobox._all_values = combo_values

    def on_keyrelease(event):
        # Filter values based on typed text
        value = event.widget.get()
        if value == '':
            event.widget['values'] = event.widget._all_values
        else:
            data = []
            for item in event.widget._all_values:
                if value.lower() in item.lower():
                    data.append(item)
            event.widget['values'] = data
            
    combobox.bind('<KeyRelease>', on_keyrelease)
    
    # Reset values on dropdown open to show full list if empty or match
    def on_post(event):
         if not var.get():
             combobox['values'] = combobox._all_values

    combobox.bind('<<ComboboxSelected>>', lambda e: None) # Default behavior
    combobox.bind('<Button-1>', on_post)

    return (var, label_to_value)


def create_multi_select(parent, options, current_value=None, editable=True):
    """
    Creates a checkable list for multi-selection.
    Returns a tuple: (StringVar, None) - StringVar holds comma-separated values.
    """
    # Parse current value (comma-separated string)
    selected_values = set()
    if current_value:
        try:
            for v in str(current_value).split(','):
                if v.strip():
                    selected_values.add(v.strip())
        except:
            pass
            
    # Process options
    choices = []
    if options and isinstance(options, list):
        if len(options) > 0 and isinstance(options[0], dict):
            for opt in options:
                choices.append({"label": str(opt["label"]), "value": str(opt["value"])})
        else:
            for opt in options:
                choices.append({"label": str(opt), "value": str(opt)})
                
    # Create widget
    container = tk.Frame(parent, bg="white")
    container.pack(fill=tk.X, expand=True)

    # Add Search bar
    search_var = tk.StringVar()
    search_entry = tk.Entry(container, textvariable=search_var)
    search_entry.pack(fill=tk.X, pady=(0, 5))
    
    frame = tk.Frame(container, borderwidth=1, relief="sunken", bg="white")
    frame.pack(fill=tk.X, expand=True)
    
    canvas = tk.Canvas(frame, height=100, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="white")
    
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    vars_map = {} # val -> BooleanVar
    cb_widgets = {} # val -> widget
    
    def on_change(*args):
        # Update result string
        vals = [val for val, var in vars_map.items() if var.get()]
        result_var.set(",".join(vals))

    result_var = tk.StringVar(value=",".join(selected_values))
    
    for choice in choices:
        val = choice["value"]
        lbl = choice["label"]
        var = tk.BooleanVar(value=(val in selected_values))
        var.trace_add("write", on_change)
        vars_map[val] = var
        
        cb = tk.Checkbutton(scroll_frame, text=lbl, variable=var, bg="white", anchor="w")
        if not editable:
            cb.config(state="disabled")
        cb.pack(fill="x", padx=2)
        cb_widgets[val] = (cb, lbl)

    def filter_list(*args):
        query = search_var.get().lower()
        for val, (cb, lbl) in cb_widgets.items():
            if query in lbl.lower():
                cb.pack(fill="x", padx=2)
            else:
                cb.pack_forget()

    search_var.trace_add("write", filter_list)
        
    return (result_var, None)


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
