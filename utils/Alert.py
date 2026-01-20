import tkinter as tk
from tkinter import messagebox

class Alert:
    @staticmethod
    def show(type, message=None, title=None):
        """
        Base method to show a custom styled popup.
        """
        # 1. Default Messages
        defaults = {
            "success": "Operation completed successfully.",
            "error": "An error occurred while processing your request.",
            "info": "Information update.",
            "warning": "Please check your inputs."
        }
        
        # 2. Handle Custom vs Default message
        if not message:
            message = defaults.get(type, "Notice.")

        # 3. Create Custom Popup Window
        root = tk._default_root
        if not root:
            # Fallback to native if no root
            messagebox.showinfo(title or type.title(), str(message))
            return

        popup = tk.Toplevel(root)
        popup.title(title or type.title())
        popup.attributes("-topmost", True)
        popup.grab_set()  # Modal
        popup.resizable(False, False)

        # Center on screen
        width = 450
        height = 250
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        # Colors & Styling
        bg_colors = {
            "success": "#d4edda",
            "error": "#f8d7da",
            "info": "#d1ecf1",
            "warning": "#fff3cd"
        }
        text_colors = {
            "success": "#155724",
            "error": "#721c24",
            "info": "#0c5460",
            "warning": "#856404"
        }
        accent_colors = {
            "success": "#28a745",
            "error": "#dc3545",
            "info": "#17a2b8",
            "warning": "#ffc107"
        }

        color_bg = bg_colors.get(type, "#f8f9fa")
        color_text = text_colors.get(type, "#212529")
        color_accent = accent_colors.get(type, "#6c757d")

        popup.config(bg=color_bg)

        # Icon/Status Label
        tk.Label(
            popup, 
            text=type.upper(), 
            font=("Arial", 12, "bold"), 
            bg=color_bg, 
            fg=color_accent,
            pady=10
        ).pack()

        # Content Container (Scrollable Text)
        text_frame = tk.Frame(popup, bg=color_bg)
        text_frame.pack(fill="both", expand=True, padx=20, pady=5)

        text_widget = tk.Text(
            text_frame, 
            wrap="word", 
            font=("Arial", 10), 
            bg=color_bg, 
            fg=color_text,
            borderwidth=0,
            highlightthickness=0,
            height=6
        )
        text_widget.pack(fill="both", expand=True)
        
        # Tags for bolding
        text_widget.tag_configure("bold", font=("Arial", 10, "bold"))

        # Format and insert content
        if isinstance(message, dict):
            for field, errs in message.items():
                # Format field name: bold and capitalized
                field_label = field.replace("_", " ").title()
                text_widget.insert("end", "• ", "")
                text_widget.insert("end", f"{field_label}: ", "bold")
                
                if isinstance(errs, list):
                    text_widget.insert("end", f"{', '.join(map(str, errs))}\n")
                else:
                    text_widget.insert("end", f"{str(errs)}\n")
        elif isinstance(message, list):
            for m in message:
                text_widget.insert("end", f"• {str(m)}\n")
        else:
            text_widget.insert("end", str(message))

        text_widget.config(state="disabled")

        # Close Button
        btn_frame = tk.Frame(popup, bg=color_bg, pady=10)
        btn_frame.pack(fill="x")

        close_btn = tk.Button(
            btn_frame, 
            text="OK", 
            command=popup.destroy,
            bg=color_accent,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            relief="flat"
        )
        close_btn.pack()

    @staticmethod
    def success(message=None, title="Success"):
        Alert.show("success", message, title)

    @staticmethod
    def error(message=None, title="Error"):
        Alert.show("error", message, title)

    @staticmethod
    def info(message=None, title="Information"):
        Alert.show("info", message, title)

    @staticmethod
    def warning(message=None, title="Warning"):
        Alert.show("warning", message, title)
