# views/crud_builder/dropdown_options_form.py
import tkinter as tk
from tkinter import ttk

class DropdownOptionsForm(tk.Toplevel):
    def __init__(self, parent, initial_options=None, callback=None, **kwargs):
        super().__init__(parent)
        self.title("Manage Dropdown Options")
        self.geometry("400x500")
        self.callback = callback
        
        self.options_rows = []
        
        self._setup_ui()
        
        if initial_options:
            for opt in initial_options:
                # opt can be {"label": "...", "value": "..."} or just a string
                if isinstance(opt, dict):
                    self.add_option_row(opt.get("label", ""), opt.get("value", ""))
                else:
                    self.add_option_row(str(opt), str(opt))
        else:
            self.add_option_row()

    def _setup_ui(self):
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="Define options for this dropdown:", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        # Scrollable Area
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Headers
        tk.Label(self.scrollable_frame, text="Label", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.scrollable_frame, text="Value", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=5)
        
        # Action Buttons
        btn_frame = tk.Frame(self, pady=10)
        btn_frame.pack(fill="x", side="bottom")
        
        tk.Button(btn_frame, text="+ Add Option", command=self.add_option_row).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Save Options", command=self.submit, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=20)

    def add_option_row(self, label="", value=""):
        row_idx = len(self.options_rows) + 1
        
        label_var = tk.StringVar(value=label)
        value_var = tk.StringVar(value=value)
        
        # Auto-fill value from label if value is empty and typing label
        def on_label_change(*args, lv=label_var, vv=value_var):
            if not vv.get():
                vv.set(lv.get())
        
        label_var.trace_add("write", on_label_change)
        
        label_entry = tk.Entry(self.scrollable_frame, textvariable=label_var, width=15)
        value_entry = tk.Entry(self.scrollable_frame, textvariable=value_var, width=15)
        delete_btn = tk.Button(self.scrollable_frame, text="X", command=lambda r=row_idx: self.delete_row(r), fg="red")
        
        label_entry.grid(row=row_idx, column=0, padx=5, pady=2)
        value_entry.grid(row=row_idx, column=1, padx=5, pady=2)
        delete_btn.grid(row=row_idx, column=2, padx=5, pady=2)
        
        self.options_rows.append({
            "idx": row_idx,
            "label_var": label_var,
            "value_var": value_var,
            "widgets": [label_entry, value_entry, delete_btn]
        })

    def delete_row(self, idx):
        for row in self.options_rows:
            if row["idx"] == idx:
                for w in row["widgets"]:
                    w.destroy()
                self.options_rows.remove(row)
                break

    def submit(self):
        options = []
        for row in self.options_rows:
            lbl = row["label_var"].get().strip()
            val = row["value_var"].get().strip()
            if lbl:
                options.append({"label": lbl, "value": val})
        
        if self.callback:
            self.callback(options)
        self.destroy()
