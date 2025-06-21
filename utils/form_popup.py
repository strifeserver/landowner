import tkinter as tk

def open_form_popup(title, field_definitions, on_submit=None, initial_data=None):
    popup = tk.Toplevel()
    popup.title(title)

    entries = {}

    for idx, (field, meta) in enumerate(sorted(field_definitions.items(), key=lambda x: x[1]["order"])):
        if meta.get("is_hidden"):
            continue  # skip hidden fields

        label = tk.Label(popup, text=meta.get("alias", field))
        label.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

        entry = tk.Entry(popup, width=30)
        entry_value = initial_data.get(field, "") if initial_data else ""
        entry.insert(0, str(entry_value))
        entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
        entries[field] = entry

    def submit():
        data = {field: entry.get() for field, entry in entries.items()}
        if on_submit:
            on_submit(data)
        popup.destroy()

    tk.Button(popup, text="Submit", command=submit).grid(row=idx + 1, column=0, columnspan=2, pady=10)

    return popup
