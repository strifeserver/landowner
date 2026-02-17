# main_window.py
import tkinter as tk
from models.navigation import Navigation
from models.Setting import Setting
from views.right_panel import RightPanel


class AnimatedLabel(tk.Label):
    """A Label that can display an animated GIF using ImageManager for caching."""
    def __init__(self, master, file_path, size=(150, 150), **kwargs):
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
            
        # If not viewable, stop the loop (it will affect restart on Map)
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
        """Resume animation when window is shown again."""
        if not self._is_animating and self.frames and len(self.frames) > 1:
            self.animate()

    def _pause_animation(self, event=None):
        """Pause animation when window is hidden."""
        # The next animate call will check winfo_viewable and stop itself, 
        # but we can also cancel pending after calls here for immediate effect (optional)
        pass

    def stop_animation(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except:
                pass
            self._after_id = None
            self._is_animating = False

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        # Custom App Name
        app_name_setting = Setting.index(filters={"setting_name": "app_name"})
        app_name = app_name_setting[0].setting_value if app_name_setting else "LandOwner"
        self.root.title(f"{app_name} - Main Window")

        # Window Size & Centering
        WindowSize = Setting.index(filters={"setting_name": "window_size"})
        size_str = WindowSize[0].setting_value if WindowSize else "800x600"
        
        try:
            width, height = map(int, size_str.split('x'))
        except ValueError:
            width, height = 800, 600

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x_c = int((screen_width / 2) - (width / 2))
        y_c = int((screen_height / 2) - (height / 2))
        
        self.root.geometry(f"{width}x{height}+{x_c}+{y_c}")

        # Global Improvement: Close focus-dependent popups (like datepickers) when clicking outside
        self.root.bind_all("<Button-1>", lambda e: e.widget.focus_set() if hasattr(e.widget, 'focus_set') else None)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)

        # Left frame (navigation)
        self.left_frame = tk.Frame(self.root, bg="#e0e0e0", width=180)
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.left_frame.grid_propagate(False)  # <- prevent auto resizing

        # User Info
        self.user_info_frame = tk.Frame(self.left_frame, bg="#e0e0e0")
        self.user_info_frame.pack(fill="x", pady=(20, 5), padx=10)

        self.lbl_username = tk.Label(
            self.user_info_frame, 
            text="", 
            bg="#e0e0e0", 
            fg="black", 
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        self.lbl_username.pack(fill="x")

        self.lbl_access_level = tk.Label(
            self.user_info_frame, 
            text="", 
            bg="#e0e0e0", 
            fg="#666666", 
            font=("Arial", 9),
            anchor="w"
        )
        self.lbl_access_level.pack(fill="x")

        tk.Label(
            self.left_frame,
            text="Navigation",
            bg="#e0e0e0",
            font=("Arial", 10, "bold"),
        ).pack(pady=(10, 5))

        # Container for dynamic menu items (Middle part)
        self.menu_container = tk.Frame(self.left_frame, bg="#e0e0e0")
        self.menu_container.pack(fill="both", expand=True)

        # Footer (Logout Section)
        self.footer_frame = tk.Frame(self.left_frame, bg="#e0e0e0", pady=20)
        self.footer_frame.pack(side="bottom", fill="x")

        # Separator line above logout
        tk.Frame(self.footer_frame, bg="#c0c0c0", height=1).pack(fill="x", padx=15, pady=(0, 15))

        self.btn_logout = tk.Button(
            self.footer_frame,
            text="Logout",
            bg="#f5f5f5",
            fg="#c0392b",
            font=("Arial", 9, "bold"),
            command=self._handle_logout
        )
        self.btn_logout.pack(padx=20, fill="x")

        # Right panel (content)
        self.right_panel = RightPanel(self.root, width=640)
        self.right_panel.grid(row=0, column=1, sticky="nswe")

        # State
        self.child_frames = {}       # parent_id -> Frame
        self.expanded_parents = {}   # parent_id -> bool

        # Subscribe to session permission changes (to auto-refresh menu)
        from utils.session import Session
        Session.subscribe(self.load_navigation)
        
        self.load_navigation()
        self.redirect_to_dashboard()

        self.root.mainloop()

    def redirect_to_dashboard(self):
        """Initial redirect to dashboard if it exists and no content is loaded."""
        all_menu_items = Navigation.index()
        dashboard_nav = next((i for i in all_menu_items if i.navigation == "dashboard"), None)
        if dashboard_nav:
            self.on_menu_click(dashboard_nav.navigation, dashboard_nav.controller, dashboard_nav.menu_name)

    # --------------------------------------------------
    # Navigation Loader
    # --------------------------------------------------
    # --------------------------------------------------
    # Navigation Loader
    # --------------------------------------------------
    def load_navigation(self):
        import os
        from utils.session import Session
        from models.access_level import AccessLevel
        from models.Setting import Setting

        # --------------------------------------------------
        # 1. Update Current Logged-In Section (User Info Frame)
        # --------------------------------------------------
        # Clear existing
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()

        # Fetch Settings
        header_setting = Setting.index(filters={"setting_name": "default_current_logged_in_display_header"})
        subheader_setting = Setting.index(filters={"setting_name": "default_current_logged_in_sub_header"})
        image_setting = Setting.index(filters={"setting_name": "default_current_logged_in_image"})

        user = Session.get_user()
        display_header = user.name if user and user.name else (header_setting[0].setting_value if header_setting else "LandOwner")
        sub_header = user.access_level_name if user else (subheader_setting[0].setting_value if subheader_setting else "Admin Panel")
        
        # Priority: 1. User display_photo, 2. setting default
        image_filename = user.display_photo if user and user.display_photo else (image_setting[0].setting_value if image_setting else None)
        

        # Image Logic
        if image_filename:
            try:
                from utils.paths import get_asset_path
                image_path = get_asset_path("images", image_filename)
                
                if os.path.exists(image_path):
                    # 1. Stop and clear previous animated image if it exists
                    if hasattr(self, "user_anim_label") and self.user_anim_label:
                        self.user_anim_label.destroy()
                        self.user_anim_label = None

                    # 2. Use AnimatedLabel (uses ImageManager internally)
                    self.user_anim_label = AnimatedLabel(self.user_info_frame, image_path, size=(150, 150), bg="#e0e0e0")
                    self.user_anim_label.pack(pady=(0, 5))

                    # 3. Trigger cleanup
                    import gc
                    gc.collect()
            except Exception as e:
                print(f"Error loading navigation image: {e}")

        # Display Header
        lbl_header = tk.Label(
            self.user_info_frame, 
            text=display_header, 
            bg="#e0e0e0", 
            fg="black", 
            font=("Arial", 12, "bold"),
            anchor="center"
        )
        lbl_header.pack(fill="x")

        # Sub Header
        lbl_sub = tk.Label(
            self.user_info_frame, 
            text=sub_header, 
            bg="#e0e0e0", 
            fg="#666666", 
            font=("Arial", 9),
            anchor="center"
        )
        lbl_sub.pack(fill="x")


        # --------------------------------------------------
        # 2. Navigation Items
        # --------------------------------------------------
        all_menu_items = Navigation.index()
        menu_items = []

        # Permission Filter
        user = Session.get_user()
        if user:
            # Fetch AccessLevel object for permission check
            access_level = AccessLevel.edit(user.access_level)
            if access_level:
                allowed_ids = access_level.get_permissions_list('view')
                # Filter items: keep if item.id is in allowed_ids
                menu_items = [item for item in all_menu_items if item.id in allowed_ids]
        
        # Clear existing menu container items
        for widget in self.menu_container.winfo_children():
            widget.destroy()

        # Group child menus by parent_id
        children_map = {}
        for item in menu_items:
            if item.parent_id:
                children_map.setdefault(item.parent_id, []).append(item)

        # Sort items by navigation_order? Assuming index() returns them sorted or DB does.
        # Ideally should sort by navigation_order.
        menu_items.sort(key=lambda x: (x.navigation_order or 999))

        for item in menu_items:
            if item.is_hidden:
                continue

            if item.navigation_type == "menu":
                self.render_menu(item)

            elif item.navigation_type == "parent_menu":
                self.render_parent_menu(item, children_map.get(item.id, []))
            
            elif item.navigation_type == "menu_header":
                self.render_menu_header(item)

            elif item.navigation_type == "menu_header":
                self.render_menu_header(item)

    # --------------------------------------------------
    # Renderers
    # --------------------------------------------------
    def render_menu_header(self, item):
        lbl = tk.Label(
            self.menu_container,
            text=item.menu_name.upper(),
            bg="#e0e0e0",
            fg="#888888",
            font=("Arial", 8, "bold"),
            anchor="w",
            pady=5
        )
        lbl.pack(fill="x", padx=10, pady=(10, 0))

    def render_menu(self, item):
        btn = tk.Button(
            self.menu_container,
            text=item.menu_name,
            width=22,
            anchor="w",
            command=lambda i=item: self.on_menu_click(i.navigation, i.controller, i.menu_name),
        )
        btn.pack(pady=2, padx=5)

    def render_parent_menu(self, parent, children):
        # Parent button
        btn = tk.Button(
            self.menu_container,
            text=f"▶ {parent.menu_name}",
            width=22,
            anchor="w",
            command=lambda p=parent: self.toggle_children(p.id),
        )
        btn.pack(pady=2, padx=5)

        # Child container (packed AFTER parent, hidden by default)
        child_frame = tk.Frame(self.menu_container, bg="#d0d0d0")
        child_frame._pack_after = btn  # store reference
        child_frame.pack_forget()

        self.child_frames[parent.id] = child_frame
        self.expanded_parents[parent.id] = False

        for child in children:
            child_btn = tk.Button(
                child_frame,
                text=f"   • {child.menu_name}",
                anchor="w",
                width=18,
                command=lambda c=child: self.on_menu_click(c.navigation, c.controller, c.menu_name),
            )
            child_btn.pack(pady=1, padx=16)

    # --------------------------------------------------
    # Accordion Toggle
    # --------------------------------------------------
    def toggle_children(self, parent_id):
        frame = self.child_frames.get(parent_id)
        expanded = self.expanded_parents.get(parent_id, False)

        if not frame:
            return

        if expanded:
            frame.pack_forget()
        else:
            frame.pack(after=frame._pack_after, fill="x")

        self.expanded_parents[parent_id] = not expanded

    # --------------------------------------------------
    # Click Handler
    # --------------------------------------------------
    def on_menu_click(self, navigation, controller_name, navigation_name):
        self.right_panel.render_content(navigation, controller_name, navigation_name)

    def _handle_logout(self):
        """Clears session and restarts to Login screen."""
        from utils.session import Session
        from controllers.AuthController import AuthController
        from views.login.login_view import LoginView
        from tkinter import messagebox
        
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            Session.clear_session()
            self.root.destroy()
            LoginView(AuthController)
