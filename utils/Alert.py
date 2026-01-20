import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.paths import get_image_path

class Alert:
    _icon_cache = {} # Static cache to keep references alive if needed

    @staticmethod
    def show(type, message=None, title=None, buttons=None, callbacks=None):
        """
        Base method to show a custom styled popup with SweetAlert-like aesthetics.
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
            # Fallback if no root exists
            messagebox.showinfo(title or type.title(), str(message))
            return

        popup = tk.Toplevel(root)
        popup.title(title or type.title())
        popup.attributes("-topmost", True)
        popup.grab_set()
        popup.resizable(False, False)

        # Style Configuration
        bg_color = "#ffffff"
        accent_color = {
            "success": "#28a745",
            "error": "#dc3545",
            "info": "#17a2b8",
            "warning": "#ffc107"
        }.get(type, "#6c757d")

        popup.config(bg=bg_color)

        # Center on screen
        width = 450
        height = 300 # Reduced height for more compact look
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        # --- Layout using a central wrapper to balance whitespace ---
        
        # Center wrapper to keep everything vertically balanced
        center_wrapper = tk.Frame(popup, bg=bg_color)
        center_wrapper.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)

        # 4. Icon (88x88)
        icon_frame = tk.Frame(center_wrapper, bg=bg_color, pady=5)
        icon_frame.pack(fill="x")
        
        icon_file = f"{type}.jpg"
        icon_path = get_image_path(icon_file)
        
        try:
            img = Image.open(icon_path)
            img = img.resize((88, 88), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            icon_label = tk.Label(icon_frame, image=photo, bg=bg_color)
            icon_label.image = photo  # Keep reference
            icon_label.pack()
        except Exception as e:
            print(f"Alert Icon Error: {e}")
            tk.Label(icon_frame, text="!", font=("Arial", 40, "bold"), fg=accent_color, bg=bg_color).pack()

        # 5. Title
        main_title = title if title else type.title() + "!"
        if type == "error" and not title:
             main_title = "Oops..."
             
        tk.Label(
            center_wrapper, 
            text=main_title, 
            font=("Segoe UI", 20, "bold"), # Slightly smaller font
            bg=bg_color, 
            fg="#595959",
            pady=0
        ).pack()

        # 6. Message Container
        text_frame = tk.Frame(center_wrapper, bg=bg_color)
        text_frame.pack(fill="x", padx=40, pady=2)

        text_widget = tk.Text(
            text_frame, 
            wrap="word", 
            font=("Segoe UI", 11), 
            bg=bg_color, 
            fg="#545454",
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            height=2 # Even shorter default height
        )
        text_widget.pack(fill="x")
        text_widget.tag_configure("center", justify='center')
        text_widget.tag_configure("bold", font=("Segoe UI", 11, "bold"))

        # Content insertion
        if isinstance(message, dict):
            for field, errs in message.items():
                field_label = field.replace("_", " ").title()
                text_widget.insert("end", "• ", "center")
                text_widget.insert("end", f"{field_label}: ", ("bold", "center"))
                msg_str = f"{', '.join(map(str, errs))}\n" if isinstance(errs, list) else f"{str(errs)}\n"
                text_widget.insert("end", msg_str, "center")
        elif isinstance(message, list):
            for m in message:
                text_widget.insert("end", f"• {str(m)}\n", "center")
        else:
            text_widget.insert("end", str(message), "center")

        text_widget.config(state="disabled")

        # 7. Button Area
        btn_container = tk.Frame(center_wrapper, bg=bg_color, pady=15)
        btn_container.pack(fill="x")

        button_configs = buttons or [("OK", "#7066e0", popup.destroy)]
        
        btn_frame = tk.Frame(btn_container, bg=bg_color)
        btn_frame.pack()

        for (btn_text, btn_color, btn_cmd) in button_configs:
            def create_btn_cmd(cmd=btn_cmd):
                def wrapped(event=None):
                    popup.destroy()
                    if callable(cmd):
                        cmd()
                return wrapped

            # Custom Rounded Button using Canvas
            btn_w, btn_h = 100, 38
            radius = 4 # Approx 0.25em
            
            canvas = tk.Canvas(
                btn_frame, 
                width=btn_w, 
                height=btn_h, 
                bg=bg_color, 
                highlightthickness=0,
                cursor="hand2"
            )
            canvas.pack(side="left", padx=10)

            def draw_btn(c, color, text_color="white", b_text=btn_text):
                c.delete("all")
                # Rounded rect parts
                c.create_oval(0, 0, radius*2, radius*2, fill=color, outline=color)
                c.create_oval(btn_w-radius*2, 0, btn_w, radius*2, fill=color, outline=color)
                c.create_oval(0, btn_h-radius*2, radius*2, btn_h, fill=color, outline=color)
                c.create_oval(btn_w-radius*2, btn_h-radius*2, btn_w, btn_h, fill=color, outline=color)
                c.create_rectangle(radius, 0, btn_w-radius, btn_h, fill=color, outline=color)
                c.create_rectangle(0, radius, btn_w, btn_h-radius, fill=color, outline=color)
                # Text
                c.create_text(btn_w/2, btn_h/2, text=b_text, fill=text_color, font=("Segoe UI", 10, "bold"))

            current_color = btn_color
            t_color = "white"
            if btn_color == "#ffffff":
                t_color = "#545454"
                
            draw_btn(canvas, current_color, t_color)
            
            # Hover effects
            def on_enter(e, c=canvas, clr=btn_color, tc=t_color, bt=btn_text):
                hover_clr = "#8177e6" if clr == "#7066e0" else "#f8f9fa" if clr == "#ffffff" else clr
                draw_btn(c, hover_clr, tc, b_text=bt)
                if clr == "#ffffff":
                    c.create_rectangle(1,1, btn_w-1, btn_h-1, outline="#dee2e6", width=1) # Border for white button

            def on_leave(e, c=canvas, clr=btn_color, tc=t_color, bt=btn_text):
                draw_btn(c, clr, tc, b_text=bt)
                if clr == "#ffffff":
                    c.create_rectangle(1,1, btn_w-1, btn_h-1, outline="#dee2e6", width=1)

            if btn_color == "#ffffff":
                 canvas.create_rectangle(1,1, btn_w-1, btn_h-1, outline="#dee2e6", width=1)

            canvas.bind("<Enter>", on_enter)
            canvas.bind("<Leave>", on_leave)
            canvas.bind("<Button-1>", create_btn_cmd())

    @staticmethod
    def success(message=None, title=None):
        Alert.show("success", message, title)

    @staticmethod
    def error(message=None, title=None):
        Alert.show("error", message, title)

    @staticmethod
    def info(message=None, title=None):
        Alert.show("info", message, title)

    @staticmethod
    def warning(message=None, title=None):
        Alert.show("warning", message, title)

    @staticmethod
    def confirm(message, title="Are you sure?", on_confirm=None, on_cancel=None):
        """
        Shows a confirmation dialog with Confirm and Cancel buttons.
        Uses info icon by default.
        """
        buttons = [
            ("Confirm", "#7066e0", on_confirm),
            ("Cancel", "#ffffff", on_cancel)
        ]
        Alert.show("info", message, title, buttons=buttons)
