# views/my_account/my_account_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from controllers.MyAccountController import MyAccountController
from PIL import Image, ImageTk
import os

class AnimatedLabel(tk.Label):
    """A Label that can display an animated GIF."""
    def __init__(self, master, file_path, size=(120, 120), **kwargs):
        super().__init__(master, **kwargs)
        from PIL import Image, ImageTk
        self.frames = []
        self.delay = 100
        
        try:
            with Image.open(file_path) as img:
                self.delay = img.info.get('duration', 100)
                try:
                    while True:
                        frame = img.copy()
                        frame.thumbnail(size, Image.Resampling.LANCZOS)
                        self.frames.append(ImageTk.PhotoImage(frame))
                        img.seek(len(self.frames))
                except EOFError:
                    pass
        except Exception as e:
            # Fallback if animation fails
            pass

        self.idx = 0
        self._after_id = None
        if self.frames:
            self.config(image=self.frames[0])
            if len(self.frames) > 1:
                self.animate()
        
        self.bind("<Destroy>", lambda e: self.stop_animation())

    def animate(self):
        if not self.winfo_exists():
            return
        self.idx = (self.idx + 1) % len(self.frames)
        self.config(image=self.frames[self.idx])
        self._after_id = self.after(self.delay, self.animate)

    def stop_animation(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

class MyAccountView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f5f5f5")
        self.controller = MyAccountController
        self.user = self.controller.get_current_user()
        
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = tk.Label(self, text="My Account", font=("Arial", 16, "bold"), bg="#f5f5f5", pady=20)
        header.pack(fill="x")

        # ----------------------------------------------------------------------
        # Scrollable Area Setup
        # ----------------------------------------------------------------------
        self.canvas = tk.Canvas(self, bg="#f5f5f5", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f5f5f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            # Update the width of the scrollable frame to match the canvas
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", _on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Mouse wheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # ----------------------------------------------------------------------
        # Content Container
        # ----------------------------------------------------------------------
        container = tk.Frame(self.scrollable_frame, bg="white", padx=30, pady=20, relief="ridge", borderwidth=1)
        container.pack(pady=10, padx=50, fill="both", expand=True)

        # ==========================================
        # SECTION 1: Account Information
        # ==========================================
        info_header = tk.Label(container, text="Account Information", font=("Arial", 12, "bold"), bg="white", anchor="w")
        info_header.pack(fill="x", pady=(0, 10))

        info_frame = tk.Frame(container, bg="white")
        info_frame.pack(fill="x")

        # Photo (Left side of info)
        self.photo_subframe = tk.Frame(info_frame, bg="white")
        self.photo_subframe.pack(side="left", padx=(0, 20))

        self.image_container = tk.Frame(self.photo_subframe, bg="white")
        self.image_container.pack(side="top")

        self.anim_photo = None
        self._load_photo()
        tk.Button(self.photo_subframe, text="Change Photo", command=self._change_photo).pack(side="top", pady=5)

        # Inputs (Right side of info)
        input_subframe = tk.Frame(info_frame, bg="white")
        input_subframe.pack(side="left", fill="both", expand=True)

        tk.Label(input_subframe, text="Full Name:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(input_subframe, width=35)
        self.name_entry.insert(0, self.user.name or "")
        self.name_entry.grid(row=1, column=0, sticky="w", pady=(0, 10))

        tk.Label(input_subframe, text="Email Address:", font=("Arial", 9, "bold"), bg="white").grid(row=2, column=0, sticky="w")
        self.email_entry = tk.Entry(input_subframe, width=35)
        self.email_entry.insert(0, self.user.email or "")
        self.email_entry.grid(row=3, column=0, sticky="w", pady=(0, 10))

        tk.Label(input_subframe, text="Access Level:", font=("Arial", 9, "bold"), bg="white").grid(row=4, column=0, sticky="w")
        tk.Label(input_subframe, text=self.user.access_level_name or "User", bg="white").grid(row=5, column=0, sticky="w")

        # Verification for Information (if email changed)
        # REMOVED: password requirement for info changes

        tk.Button(container, text="Save Information", command=self._save_info).pack(anchor="w", pady=10)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ==========================================
        # SECTION 2: Account Password
        # ==========================================
        pass_header = tk.Label(container, text="Account Password", font=("Arial", 12, "bold"), bg="white", anchor="w")
        pass_header.pack(fill="x", pady=(0, 10))

        pass_frame = tk.Frame(container, bg="white")
        pass_frame.pack(fill="x")

        tk.Label(pass_frame, text="New Password:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        self.pass_var = tk.StringVar()
        self.pass_var.trace_add("write", self._on_pass_change)
        self.new_pass_entry = tk.Entry(pass_frame, show="*", width=35, textvariable=self.pass_var)
        self.new_pass_entry.grid(row=1, column=0, sticky="w", pady=(0, 10))

        tk.Label(pass_frame, text="Confirm New Password:", font=("Arial", 9, "bold"), bg="white").grid(row=2, column=0, sticky="w")
        self.confirm_pass_entry = tk.Entry(pass_frame, show="*", width=35)
        self.confirm_pass_entry.grid(row=3, column=0, sticky="w", pady=(0, 10))

        tk.Label(container, text="Current Password (Required to change password):", font=("Arial", 8, "italic"), bg="white", fg="#666").pack(anchor="w")
        self.pass_curr_pass = tk.Entry(container, show="*", width=35)
        self.pass_curr_pass.pack(anchor="w", pady=(0, 10))

        self.btn_save_pass = tk.Button(container, text="Update Password", command=self._save_password, state="disabled")
        self.btn_save_pass.pack(anchor="w", pady=10)

        # ==========================================
        # SECTION 3: Logout
        # ==========================================
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)
        tk.Button(container, text="Logout", command=self._handle_logout).pack(anchor="w", pady=10)

        self.display_photo_path = None

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _handle_logout(self):
        """Clears session and restarts to Login screen."""
        from utils.session import Session
        from controllers.AuthController import AuthController
        from views.login.login_view import LoginView
        
        Session.clear_session()
        # Find the root window and destroy it
        root = self.winfo_toplevel()
        root.destroy()
        
        # Open Login View
        LoginView(AuthController)

    def _on_pass_change(self, *args):
        """Enables the password save button only when text is detected."""
        if self.pass_var.get().strip():
            self.btn_save_pass.config(state="normal")
        else:
            self.btn_save_pass.config(state="disabled")

    def _load_photo(self):
        photo_filename = self.user.display_photo or "placeholder_user.png"
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        photo_path = os.path.join(base_path, "assets", "images", photo_filename)

        if not os.path.exists(photo_path):
            photo_path = os.path.join(base_path, "assets", "images", "placeholder_user.png")

        try:
            # 1. Stop and clear existing animated photo if it exists
            if self.anim_photo:
                self.anim_photo.stop_animation()
                self.anim_photo.destroy()
                self.anim_photo = None
            
            import gc

            # 2. Use AnimatedLabel for potential GIFs
            self.anim_photo = AnimatedLabel(self.image_container, photo_path, size=(120, 120), bg="white")
            self.anim_photo.pack(fill="both", expand=True)
            
            # 3. Trigger cleanup
            gc.collect()
        except Exception as e:
            pass

    def _change_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self.display_photo_path = file_path
            
            # 1. Stop and clear existing animated photo
            if self.anim_photo:
                self.anim_photo.stop_animation()
                self.anim_photo.destroy()
                self.anim_photo = None
            
            import gc

            # 2. Load and preview the new photo safely
            try:
                self.anim_photo = AnimatedLabel(self.image_container, file_path, size=(120, 120), bg="white")
                self.anim_photo.pack(fill="both", expand=True)
                
                # 3. Trigger cleanup
                gc.collect()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def _save_info(self):
        data = {
            "name": self.name_entry.get(),
            "email": self.email_entry.get(),
            "display_photo_path": self.display_photo_path
        }
        
        result = self.controller.update_profile(data)
        if result["success"]:
            messagebox.showinfo("Success", "Account information updated")
            self.user = self.controller.get_current_user()
            self._load_photo()
        else:
            messagebox.showerror("Error", result["message"])

    def _save_password(self):
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        
        if not new_pass:
            return
            
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New passwords do not match")
            return

        data = {
            "new_password": new_pass,
            "current_password": self.pass_curr_pass.get()
        }

        result = self.controller.update_profile(data)
        if result["success"]:
            messagebox.showinfo("Success", "Password updated successfully")
            self.new_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.delete(0, tk.END)
            self.pass_curr_pass.delete(0, tk.END)
            self.user = self.controller.get_current_user()
        else:
            messagebox.showerror("Error", result["message"])
