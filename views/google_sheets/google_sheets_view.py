import tkinter as tk
from tkinter import ttk, messagebox
from models.Setting import Setting

class GoogleSheetsView(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller
        
        self.colors = {
            "primary": "#2563eb",   # Blue
            "success": "#16a34a",   # Green
            "danger": "#dc2626",    # Red
            "text": "#1e293b",
            "muted": "#64748b",
            "border": "#e2e8f0",
            "bg": "#ffffff"
        }
        
        self.setup_ui()

    def setup_ui(self):
        # 0. Create Canvas and Scrollbar for global scrolling
        self.canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8fafc")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mousewheel locally to avoid global conflicts and errors after destruction
        def _on_mousewheel(event):
            try:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        def _bind_mouse(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mouse(event):
            self.canvas.unbind_all("<MouseWheel>")

        self.canvas.bind("<Enter>", _bind_mouse)
        self.canvas.bind("<Leave>", _unbind_mouse)
        
        # Also ensure we unbind when this widget is destroyed
        self.bind("<Destroy>", _unbind_mouse)

        # Main Content container within scrollable frame
        container_full = tk.Frame(self.scrollable_frame, bg="#f8fafc")
        container_full.pack(fill="both", expand=True)
        
        # We need to ensure the scrollable_frame width matches the canvas width for a good look
        def _on_canvas_configure(event):
            # Update the width of the scrollable_frame to fill the canvas
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Header
        header_frame = tk.Frame(container_full, bg="white", padx=30, pady=25, highlightbackground=self.colors["border"], highlightthickness=1)
        header_frame.pack(fill="x", side="top", pady=(0, 20))
        
        tk.Label(
            header_frame, 
            text="Google Sheets Integration", 
            font=("Arial", 16, "bold"), 
            bg="white", 
            fg=self.colors["text"]
        ).pack(anchor="w")
        
        tk.Label(
            header_frame, 
            text="Test your connection and access permissions for Google Sheets integration.", 
            font=("Arial", 10), 
            bg="white", 
            fg=self.colors["muted"]
        ).pack(anchor="w", pady=(5, 0))

        # Content Card
        self.content_container = tk.Frame(container_full, bg="#f8fafc", padx=30)
        self.content_container.pack(fill="both", expand=True)

        # 📚 Setup Guide Section
        guide_card = tk.Frame(self.content_container, bg="white", padx=30, pady=25, highlightbackground=self.colors["border"], highlightthickness=1)
        guide_card.pack(fill="x", pady=(0, 20))

        tk.Label(guide_card, text="Setup Guide & Troubleshooting", font=("Arial", 12, "bold"), bg="white", fg=self.colors["text"]).pack(anchor="w", pady=(0, 15))

        # Scrollable Text Area for Guide
        guide_inner_frame = tk.Frame(guide_card, bg="white")
        guide_inner_frame.pack(fill="x", expand=True)

        guide_scrollbar = tk.Scrollbar(guide_inner_frame)
        guide_scrollbar.pack(side="right", fill="y")

        guide_text = tk.Text(
            guide_inner_frame, 
            height=12, 
            font=("Consolas", 10), 
            bg="#f8fafc", 
            fg="#334155",
            padx=15, 
            pady=15,
            borderwidth=1,
            relief="flat",
            yscrollcommand=guide_scrollbar.set
        )
        guide_text.pack(side="left", fill="x", expand=True)
        guide_scrollbar.config(command=guide_text.yview)

        guide_content = """GOOGLE SHEETS API – FULL SETUP + FIX SERVICE_DISABLED
(Local Program Integration Guide)

PART 1 — INITIAL SETUP (FROM SCRATCH)

STEP 1 — Create / Select Google Cloud Project
Go to: https://console.cloud.google.com/
Click the Project Dropdown (top left).
1. Click "New Project" → Create one
Make sure you remember the project name.

STEP 2 — Enable Required APIs
Go to: https://console.cloud.google.com/apis/library
Enable the following APIs:
- Google Sheets API
- Google Drive API
Click each one → Press ENABLE.
Wait 1–2 minutes after enabling.

STEP 3 — Create Service Account
Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
Click "Create Service Account"
- Give it a name (Example: sheets-access)
- Click Create and Continue
- Role: Select "Editor" (simple setup)
- Click Done

STEP 4 — Create Service Account JSON Key
- Click the Service Account you just created.
- Go to the "Keys" tab.
- Click "Add Key" → "Create New Key"
- Select JSON → Click Create
- The JSON file will download automatically.
- Save it inside your project folder.

STEP 5 — Share Google Sheet With Service Account
- Open your Google Sheet → Click Share.
- Copy the email inside your JSON file (example: something@project-id.iam.gserviceaccount.com)
- Paste it in the Share box → Give it Editor access → Click Send.
This step is REQUIRED.

PART 2 — FIXING "SERVICE_DISABLED" ERROR

ERROR: SERVICE_DISABLED
Meaning: The API you are calling is not enabled in the project linked to your JSON.

FIX STEP 1 — Confirm Correct Project
- Open your JSON file and look for "project_id".
- Go to: https://console.cloud.google.com/
- The project at the top MUST match the project_id in your JSON.

FIX STEP 2 — Verify APIs Are Enabled
- Go to: https://console.cloud.google.com/apis/library
- Search for: Google Sheets API & Google Drive API
- Both must say ENABLED. If not, click Enable.

FIX STEP 3 — Wait 1–2 Minutes
- Google sometimes delays activation. Wait 60 seconds before trying again.

FIX STEP 4 — If Still Failing
- Check: Correct JSON file? Same project? Sheet shared?
- If needed: Delete old keys and create a new JSON key.

QUICK TROUBLESHOOT CHECKLIST
[ ] Correct project selected
[ ] Sheets API enabled
[ ] Drive API enabled
[ ] Sheet shared with service account
[ ] Waited 1–2 minutes
[ ] Using correct JSON file
"""
        guide_text.insert("1.0", guide_content)
        guide_text.config(state="disabled")

        card = tk.Frame(self.content_container, bg="white", padx=30, pady=30, highlightbackground=self.colors["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 20))
        
        tk.Label(card, text="Connection Test", font=("Arial", 12, "bold"), bg="white", fg=self.colors["text"]).pack(anchor="w", pady=(0, 20))

        # Current Settings Display
        settings_frame = tk.Frame(card, bg="#f1f5f9", padx=20, pady=20)
        settings_frame.pack(fill="x", pady=(0, 25))
        
        # Load settings for display
        sa_setting = Setting.index(filters={"setting_name": "google_service_account"})
        id_setting = Setting.index(filters={"setting_name": "google_sheet_id"})
        
        sa_status = "Configured" if sa_setting and sa_setting[0].setting_value else "Missing"
        id_val = id_setting[0].setting_value if id_setting else "Not Set"

        self.add_setting_row(settings_frame, "Service Account JSON:", sa_status)
        self.add_setting_row(settings_frame, "Target Sheet ID:", id_val)

        # Validation Button
        self.btn_validate = tk.Button(
            card, 
            text="Validate Connection", 
            command=self.on_validate, 
            bg=self.colors["primary"], 
            fg="white", 
            font=("Arial", 10, "bold"),
            padx=25, 
            pady=10,
            cursor="hand2",
            relief="flat"
        )
        self.btn_validate.pack(anchor="w")

        # Results Section (Initially Hidden)
        self.results_frame = tk.Frame(card, bg="white", pady=25)
        # We don't pack it yet

    def add_setting_row(self, parent, label, value):
        row = tk.Frame(parent, bg="#f1f5f9", pady=5)
        row.pack(fill="x")
        tk.Label(row, text=label, font=("Arial", 9, "bold"), bg="#f1f5f9", fg=self.colors["muted"], width=20, anchor="w").pack(side="left")
        tk.Label(row, text=value, font=("Arial", 9), bg="#f1f5f9", fg=self.colors["text"], anchor="w").pack(side="left", fill="x", expand=True)

    def on_validate(self):
        # Import helpers locally if preferred or at top-level
        from utils.thread_manager import ThreadManager
        from utils.alert import Alert
        
        # Initialize thread manager if not exists
        if not hasattr(self, 'thread_manager'):
            self.thread_manager = ThreadManager(self)

        # UI Disable
        self.btn_validate.config(state="disabled")
        
        # Show Overlay
        loading_popup = Alert.loading("Connecting to Google Sheets...\nPlease wait.", "Connecting")
        
        def run_validation():
            if self.controller:
                return self.controller.validate_connection_logic()
            return {"success": False, "message": "Controller not linked."}
            
        def on_complete(result):
            if loading_popup and loading_popup.winfo_exists():
                loading_popup.destroy()
            self.btn_validate.config(state="normal")
            self.show_results(result)
            
        def on_error(e):
            if loading_popup and loading_popup.winfo_exists():
                loading_popup.destroy()
            self.btn_validate.config(state="normal")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        self.thread_manager.run_in_thread(run_validation, on_complete, on_error)

    def show_results(self, result):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        self.results_frame.pack(fill="x", pady=(10, 0))
        
        success = result.get("success", False)
        bg_color = "#f0fdf4" if success else "#fef2f2"
        border_color = "#bbf7d0" if success else "#fecaca"
        text_color = self.colors["success"] if success else self.colors["danger"]
        
        res_card = tk.Frame(self.results_frame, bg=bg_color, padx=15, pady=15, highlightbackground=border_color, highlightthickness=1)
        res_card.pack(fill="x")
        
        # Header with copy button
        header_frame = tk.Frame(res_card, bg=bg_color)
        header_frame.pack(fill="x", anchor="w")
        
        msg_header = "Validation Successful" if success else "Validation Failed"
        tk.Label(header_frame, text=msg_header, font=("Arial", 10, "bold"), bg=bg_color, fg=text_color).pack(side="left")
        
        # Copy button (only show if there's an error or detailed message)
        if not success or result.get("message"):
            copy_btn = tk.Button(
                header_frame,
                text="📋 Copy Error",
                command=lambda: self.copy_to_clipboard(result.get("message", "")),
                bg=self.colors["primary"],
                fg="white",
                font=("Arial", 8),
                padx=10,
                pady=3,
                cursor="hand2",
                relief="flat"
            )
            copy_btn.pack(side="right")
        
        tk.Label(res_card, text=result.get("message", "Unknown result"), font=("Arial", 9), bg=bg_color, fg=self.colors["text"], wraplength=600, justify="left").pack(anchor="w", pady=(5, 0))
        
        if success:
            details = f"• Read Status: {result.get('read_status')}\n• Write Status: {result.get('write_status')}"
            tk.Label(res_card, text=details, font=("Arial", 9), bg=bg_color, fg=self.colors["muted"], justify="left").pack(anchor="w", pady=(10, 0))

    def copy_to_clipboard(self, text):
        """Copy text to clipboard and show confirmation."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # Required for clipboard to work
        messagebox.showinfo("Copied", "Error message copied to clipboard!")
