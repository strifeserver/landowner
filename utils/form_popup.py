# utils/form_popup.py
import tkinter as tk

def open_form_popup(title, field_definitions, on_submit, initial_data=None):
    """
    Opens a generic form popup for creating or editing a record.

    Args:
        title (str): Popup window title
        field_definitions (dict): Field metadata (aliases, editable, options)
        on_submit (callable): Function to call on form submission
        initial_data (dict or object, optional): Pre-fill form fields
    """
    print('open_form_popup')
    print(' ')
    print(' ')
    print(field_definitions)
    print(' ')
    print(' ')

    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry("400x500")

    entries = {}
    
    for field_name, config in field_definitions.items():
        # Skip auto-managed fields
        if field_name in ("id", "created_at", "updated_at") or config.get("is_hidden"):
            continue

        label = config.get("alias", field_name)
        is_editable = config.get("editable", True)
        options = config.get("options", None)

        # ✅ Get value from initial_data whether it's a dict or object
        if isinstance(initial_data, dict):
            value = initial_data.get(field_name, "")
        elif initial_data is not None:
            value = getattr(initial_data, field_name, "")
        else:
            value = ""

        frame = tk.Frame(popup)
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame, text=label, anchor="w").pack(fill=tk.X)

        # Choose input type
        if options:
            input_widget = create_dropdown_field(frame, options, value, is_editable)
        else:
            input_widget = create_text_field(frame, value, is_editable)

        entries[field_name] = input_widget

    # Submit Button
    submit_btn = tk.Button(
        popup, text="Submit", command=lambda: handle_submit(entries, on_submit, popup)
    )
    submit_btn.pack(pady=10)


# ----------------------------
# Helper functions
# ----------------------------

def create_text_field(parent, value="", editable=True):
    """Creates a single-line text Entry widget."""
    entry = tk.Entry(parent)
    entry.insert(0, value if value is not None else "")
    if not editable:
        entry.config(state="disabled")
    entry.pack(fill=tk.X)
    return entry


from tkinter import ttk
import tkinter as tk

def create_dropdown_field(parent, options, current_value=None, editable=True):
    """
    Creates a Combobox (HTML-like Select) with optional label-to-value mapping.

    Args:
        parent (tk.Widget): Parent frame
        options (list): List of values or list of dicts {"label": str, "value": any}
        current_value (any): Current value to pre-select
        editable (bool): If False, the dropdown is readonly

    Returns:
        tuple: (tk.StringVar, dict or None) → variable and optional label_to_value map
    """
    # Check if options are objects with label/value
    is_object_list = all(isinstance(opt, dict) and "label" in opt and "value" in opt for opt in options)

    if is_object_list:
        # Build mapping
        label_to_value = {opt["label"]: opt["value"] for opt in options}
        value_to_label = {str(opt["value"]): opt["label"] for opt in options}

        # Determine default selected label
        default_label = value_to_label.get(str(current_value), next(iter(label_to_value)))
        combo_values = list(label_to_value.keys())
    else:
        label_to_value = None
        combo_values = options
        default_label = str(current_value) if current_value is not None else str(options[0])

    var = tk.StringVar(value=default_label)

    combobox = ttk.Combobox(
        parent,
        textvariable=var,
        values=combo_values,
        state="readonly" if not editable else "normal",
    )
    combobox.pack(fill=tk.X, pady=2)

    return var, label_to_value


def handle_submit(entries, on_submit, popup):
    """
    Collects all values from the form and calls the on_submit callback.
    """
    data = {}
    for field, widget in entries.items():
        if isinstance(widget, tk.Entry):
            data[field] = widget.get()
        elif isinstance(widget, tk.StringVar):
            data[field] = widget.get()
        else:
            data[field] = None

    if callable(on_submit):
        on_submit(data)

    popup.destroy()
