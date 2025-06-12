# table_filters.py

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date


def create_filter_window(self):
    filter_window = tk.Toplevel(self)
    filter_window.title("Advanced Filters")
    filter_window.geometry("300x600")
    tk.Label(filter_window, text="Enter filter values below:").pack(pady=5)

    self.filter_entries = {}
    self.date_check_vars = {}

    for col in self.columns:
        row_frame = tk.Frame(filter_window)
        row_frame.pack(fill=tk.X, padx=10, pady=5)

        label_text = (
            self.column_labels[self.columns.index(col)] if self.column_labels else col
        )

        if col in ["created_at", "updated_at"]:
            var = tk.BooleanVar(value=False)
            self.date_check_vars[col] = var

            cb = tk.Checkbutton(row_frame, text=label_text, variable=var)
            cb.pack(side=tk.LEFT)

            entry = DateEntry(
                row_frame, date_pattern="yyyy-mm-dd", width=16, state="disabled"
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            def toggle_entry_state(var=var, entry=entry):
                entry.config(state="normal" if var.get() else "disabled")

            var.trace_add(
                "write",
                lambda *args, var=var, entry=entry: toggle_entry_state(var, entry),
            )
        else:
            tk.Label(row_frame, text=label_text + ":", width=12, anchor="w").pack(
                side=tk.LEFT
            )
            entry = tk.Entry(row_frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.filter_entries[col] = entry

    # Date Range Section
    self.enable_range_var = tk.BooleanVar(value=False)

    range_checkbox = tk.Checkbutton(
        filter_window,
        text="Enable Created At Range",
        variable=self.enable_range_var,
    )
    range_checkbox.pack(pady=5)

    from_frame = tk.Frame(filter_window)
    from_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(from_frame, text="Created At From:", width=14, anchor="w").pack(
        side=tk.LEFT
    )
    self.created_at_from = DateEntry(
        from_frame, date_pattern="yyyy-mm-dd", width=16, state="disabled"
    )
    self.created_at_from.pack(side=tk.LEFT, fill=tk.X, expand=True)

    to_frame = tk.Frame(filter_window)
    to_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(to_frame, text="Created At To:", width=14, anchor="w").pack(side=tk.LEFT)
    self.created_at_to = DateEntry(
        to_frame, date_pattern="yyyy-mm-dd", width=16, state="disabled"
    )
    self.created_at_to.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def toggle_created_range():
        if self.enable_range_var.get():
            self.created_at_from.config(state="normal")
            self.created_at_to.config(state="normal")
            self.created_at_from.set_date(date.today())
            self.created_at_to.set_date(date.today())
        else:
            self.created_at_from.config(state="disabled")
            self.created_at_to.config(state="disabled")
            self.created_at_from.delete(0, tk.END)
            self.created_at_to.delete(0, tk.END)

    self.enable_range_var.trace_add("write", lambda *args: toggle_created_range())

    tk.Button(
        filter_window, text="Apply Filters", command=self.apply_advanced_filters
    ).pack(pady=10)


def apply_advanced_filters(self):
    filters = {}

    for col, entry in self.filter_entries.items():
        val = entry.get().strip()
        if col in ["created_at", "updated_at"]:
            if self.date_check_vars[col].get() and val:
                filters[col] = val
        else:
            if val:
                filters[col] = val.lower()

    if self.enable_range_var.get():
        from_val = self.created_at_from.get().strip()
        to_val = self.created_at_to.get().strip()
        if from_val:
            filters["created_at_from"] = from_val
        if to_val:
            filters["created_at_to"] = to_val

    if self.controller_callback:
        self.filtered_data = self.controller_callback(filters=filters)
    else:
        self.filtered_data = [
            row
            for row in self.original_data
            if all(
                str(row.get(col, "")).lower().find(val) != -1
                for col, val in filters.items()
                if col not in ["created_at_from", "created_at_to"]
            )
        ]

    self.render_rows()
