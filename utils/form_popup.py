import tkinter as tk
from tkinter import ttk


def open_form_popup(title, field_definitions, on_submit, initial_data=None):
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
        value = (initial_data or {}).get(field_name, "")

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


# --- Helpers ---


def create_dropdown_field(parent, options, current_value, editable):
    """Creates a dropdown (Combobox) with label-to-value mapping support."""
    is_object_list = all(
        isinstance(opt, dict) and "label" in opt and "value" in opt for opt in options
    )

    if is_object_list:
        label_to_value = {opt["label"]: opt["value"] for opt in options}
        value_to_label = {str(opt["value"]): opt["label"] for opt in options}
        default_label = value_to_label.get(
            str(current_value), next(iter(label_to_value))
        )
        var = tk.StringVar(value=default_label)
        combo_values = list(label_to_value.keys())
    else:
        label_to_value = None
        combo_values = options
        var = tk.StringVar(
            value=str(current_value) if current_value else str(options[0])
        )

    combobox = ttk.Combobox(
        parent,
        textvariable=var,
        values=combo_values,
        state="readonly" if not editable else "normal",
    )
    combobox.pack(fill=tk.X)

    return (var, label_to_value)


def create_text_field(parent, value, editable):
    """Creates a simple text entry field."""
    entry = tk.Entry(parent)
    entry.insert(0, str(value))
    entry.configure(state="normal" if editable else "readonly")
    entry.pack(fill=tk.X)
    return entry


def handle_submit(entries, on_submit, popup):
    """Processes form values and calls the on_submit callback."""
    data = {}
    for key, widget in entries.items():
        if isinstance(widget, tuple):  # dropdown
            var, label_map = widget
            selected = var.get()
            data[key] = label_map[selected] if label_map else selected
        elif isinstance(widget, tk.Entry):
            data[key] = widget.get()
        elif isinstance(widget, tk.StringVar):
            data[key] = widget.get()

    popup.destroy()
    on_submit(data)
