import tkinter as tk
from tkcalendar import DateEntry
from datetime import date


def setup_date_filters(self, window):
    def bind_default_date(entry):
        def on_focus(event):
            if not entry.get():
                entry.set_date(date.today())
        entry.bind("<FocusIn>", on_focus)

    self.enable_date_filters = tk.BooleanVar(value=False)
    tk.Checkbutton(
        window, text="Date Filters", variable=self.enable_date_filters
    ).pack(pady=(10, 5))

    self.date_filters_frame = tk.Frame(window)
    self.date_filters_frame.pack(fill=tk.X, padx=5, pady=5)

    # Date Created
    self.date_created_enabled = tk.BooleanVar(value=False)
    self.dc_frame = tk.Frame(self.date_filters_frame)
    tk.Checkbutton(
        self.dc_frame, text="Date Created", variable=self.date_created_enabled
    ).pack(side=tk.LEFT)
    self.date_created_entry = DateEntry(self.dc_frame, date_pattern="yyyy-mm-dd", width=16)
    self.date_created_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.date_created_entry)

    def toggle_dc_state(*_):
        self.date_created_entry.config(
            state="normal" if self.date_created_enabled.get() else "disabled"
        )
        if not self.date_created_enabled.get():
            self.date_created_entry.delete(0, tk.END)
        if self.date_created_enabled.get():
            self.enable_range_var.set(False)
    self.date_created_enabled.trace_add("write", toggle_dc_state)
    toggle_dc_state()

    # Date Updated
    self.date_updated_enabled = tk.BooleanVar(value=False)
    self.du_frame = tk.Frame(self.date_filters_frame)
    tk.Checkbutton(
        self.du_frame, text="Date Updated", variable=self.date_updated_enabled
    ).pack(side=tk.LEFT)
    self.date_updated_entry = DateEntry(self.du_frame, date_pattern="yyyy-mm-dd", width=16)
    self.date_updated_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.date_updated_entry)

    def toggle_du_state(*_):
        self.date_updated_entry.config(
            state="normal" if self.date_updated_enabled.get() else "disabled"
        )
        if not self.date_updated_enabled.get():
            self.date_updated_entry.delete(0, tk.END)
        if self.date_updated_enabled.get():
            self.enable_range_var.set(False)
    self.date_updated_enabled.trace_add("write", toggle_du_state)
    toggle_du_state()

    # Date Range
    self.enable_range_var = tk.BooleanVar(value=False)
    self.range_toggle = tk.Checkbutton(
        self.date_filters_frame,
        text="Enable Date Created Range",
        variable=self.enable_range_var,
    )

    self.range_frame = tk.Frame(self.date_filters_frame)

    # From
    from_frame = tk.Frame(self.range_frame)
    tk.Label(from_frame, text="From:", width=10, anchor="w").pack(side=tk.LEFT)
    self.created_at_from = DateEntry(from_frame, date_pattern="yyyy-mm-dd", width=16)
    self.created_at_from.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.created_at_from)

    # To
    to_frame = tk.Frame(self.range_frame)
    tk.Label(to_frame, text="To:", width=10, anchor="w").pack(side=tk.LEFT)
    self.created_at_to = DateEntry(to_frame, date_pattern="yyyy-mm-dd", width=16)
    self.created_at_to.pack(side=tk.LEFT, fill=tk.X, expand=True)
    bind_default_date(self.created_at_to)

    def toggle_range_state(*_):
        state = "normal" if self.enable_range_var.get() else "disabled"
        for entry in [self.created_at_from, self.created_at_to]:
            entry.config(state=state)
            if state == "disabled":
                entry.delete(0, tk.END)
        if self.enable_range_var.get():
            self.date_created_enabled.set(False)
            self.date_updated_enabled.set(False)
    self.enable_range_var.trace_add("write", toggle_range_state)
    toggle_range_state()

    # Add from/to to frame
    from_frame.pack(fill=tk.X, pady=2)
    to_frame.pack(fill=tk.X, pady=2)

    # Show/hide logic
    def toggle_date_filters(*_):
        if self.enable_date_filters.get():
            self.dc_frame.pack(fill=tk.X, padx=10, pady=2)
            self.du_frame.pack(fill=tk.X, padx=10, pady=2)
            self.range_toggle.pack(anchor="w", padx=10, pady=5)
            self.range_frame.pack(fill=tk.X, padx=10, pady=2)
        else:
            self.dc_frame.pack_forget()
            self.du_frame.pack_forget()
            self.range_toggle.pack_forget()
            self.range_frame.pack_forget()
    self.enable_date_filters.trace_add("write", toggle_date_filters)
    toggle_date_filters()
