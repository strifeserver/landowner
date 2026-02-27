# views/login_view.py
import tkinter as tk
from tkinter import messagebox
from views.main_window import MainWindow  # Make sure this import works correctly

class AnimatedLabel(tk.Label):
    """A Label that can display an animated GIF using ImageManager for caching."""
    def __init__(self, master, file_path, size=(120, 120), **kwargs):
        super().__init__(master, **kwargs)
        from utils.ImageManager import ImageManager
        
        self.frames, self.delay = ImageManager.get_gif(file_path, size)
        
        self.idx = 0
        self._after_id = None
        self._is_animating = False
        
        if self.frames:
            self.config(image=self.frames[0])
            if len(self.frames) > 1:
                self.animate()
                # Bind visibility events to pause/resume animation
                self.bind("<Map>", self._resume_animation)
                self.bind("<Unmap>", self._pause_animation)
        
        self.bind("<Destroy>", lambda e: self.stop_animation())

    def animate(self):
        if not self.winfo_exists() or not self.frames:
            return
            
        # If not viewable, stop the loop
        if not self.winfo_viewable():
            self._is_animating = False
            return

        self._is_animating = True
        self.idx = (self.idx + 1) % len(self.frames)
        try:
            self.config(image=self.frames[self.idx])
            self._after_id = self.after(self.delay, self.animate)
        except:
            pass

    def _resume_animation(self, event=None):
        if not self._is_animating and self.frames and len(self.frames) > 1:
            self.animate()

    def _pause_animation(self, event=None):
        pass

    def stop_animation(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except:
                pass
            self._after_id = None
            self._is_animating = False

class LoginView:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Login")
        
        # Set Application Icon
        try:
            import os
            # Calculate base path: views/login/login_view.py -> views/login -> views -> root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base_dir, "assets", "images", "Strife.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            # print(f"Failed to set icon: {e}")
            pass

        
        # Load Settings for Branding
        from models.Setting import Setting
        app_name_set = Setting.index(filters={"setting_name": "app_name"})
        app_logo_set = Setting.index(filters={"setting_name": "app_logo"})
        
        app_name = app_name_set[0].setting_value if app_name_set else "MerchantCMS"
        logo_filename = app_logo_set[0].setting_value if app_logo_set else None

        self.root.geometry("400x500")
        self.root.config(bg="#f5f5f5")

        # Main Container
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Branding Section
        if logo_filename:
            try:
                import os
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                logo_path = os.path.join(base_path, "assets", "images", logo_filename)
                
                if os.path.exists(logo_path):
                    # Use AnimatedLabel for potential GIFs
                    self.logo_label = AnimatedLabel(main_frame, logo_path, size=(120, 120), bg="#f5f5f5")
                    self.logo_label.pack(pady=(0, 10))
            except Exception as e:
                pass

        tk.Label(main_frame, text=app_name, font=("Arial", 18, "bold"), bg="#f5f5f5").pack(pady=(0, 30))

        # Form
        tk.Label(main_frame, text="Username", bg="#f5f5f5", font=("Arial", 10)).pack(pady=2, anchor="w")
        self.username_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.username_entry.pack(pady=(0, 10))

        tk.Label(main_frame, text="Password", bg="#f5f5f5", font=("Arial", 10)).pack(pady=2, anchor="w")
        self.password_entry = tk.Entry(main_frame, show="*", width=30, font=("Arial", 10))
        self.password_entry.pack(pady=(0, 20))

        button_frame = tk.Frame(main_frame, bg="#f5f5f5")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Login", command=self.handle_login, width=10).pack(side=tk.LEFT, padx=10)

        # 🔑 Check for Quick Login (active session)
        from utils.session import Session
        if Session.load_session():
            tk.Button(
                button_frame, 
                text="Quick Login", 
                bg="#e1f5fe", 
                command=self.handle_quick_login
            ).pack(side=tk.LEFT, padx=10)

        # 🔑 Bind the Enter/Return key to the login handler
        self.root.bind('<Return>', lambda event: self.handle_login())

        self.root.mainloop()

    def handle_quick_login(self):
        """Re-enters the app using existing session."""
        from utils.session import Session
        from utils.alert import Alert
        user = Session.get_user()
        if user:
            Alert.success(f"Welcome back, {user.username}!", title="Quick Login")
            self.root.destroy()
            MainWindow()
        else:
            messagebox.showerror("Error", "Session expired or invalid.")

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Show loading alert
        from utils.alert import Alert
        loading_popup = Alert.loading("Validating credentials...", "Logging In")
        
        # Force UI update to show loading
        self.root.update()
        
        try:
            user = self.controller.login(username, password)
            
            # Close loading popup
            if loading_popup:
                loading_popup.destroy()
            
            if user:
                from utils.session import Session
                Session.set_user(user)
                
                # Show welcome notification
                Alert.custom(
                    f"Welcome back, {user.username}! You have successfully logged in.",
                    title="Welcome!",
                    icon_type="success"
                )
                
                self.root.destroy()
                MainWindow()  # You might want to pass the controller here if needed
                
        except ValueError as e:
            # Close loading popup
            if loading_popup:
                loading_popup.destroy()
            Alert.error(str(e), "Login Failed")
        except Exception as e:
            # Close loading popup
            if loading_popup:
                loading_popup.destroy()
            Alert.error(f"An unexpected error occurred: {e}", "Error")
