# main_window.py
import tkinter as tk
from models.navigation import Navigation
from models.Setting import Setting
from views.right_panel import RightPanel


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LandOwner - Main Window")

        WindowSize = Setting.index(filters={"setting_name": "window_size"})
        self.root.geometry(WindowSize[0].setting_value if WindowSize else "800x600")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)

        # Left frame (navigation)
        self.left_frame = tk.Frame(self.root, bg="#e0e0e0", width=180)
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.left_frame.grid_propagate(False)  # <- prevent auto resizing

        tk.Label(
            self.left_frame,
            text="Navigation",
            bg="#e0e0e0",
            font=("Arial", 10, "bold"),
        ).pack(pady=10)

        # Container for dynamic menu items
        self.menu_container = tk.Frame(self.left_frame, bg="#e0e0e0")
        self.menu_container.pack(fill="both", expand=True)

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

        self.root.mainloop()

    # --------------------------------------------------
    # Navigation Loader
    # --------------------------------------------------
    # --------------------------------------------------
    # Navigation Loader
    # --------------------------------------------------
    def load_navigation(self):
        from utils.session import Session
        from models.access_level import AccessLevel

        all_menu_items = Navigation.index()
        menu_items = []

        # Permission Filter
        user = Session.get_user()
        if user:
            # Fetch AccessLevel object
            access_level = AccessLevel.edit(user.access_level)
            if access_level:
                allowed_ids = access_level.get_permissions_list('view')
                # Filter items: keep if item.id is in allowed_ids
                menu_items = [item for item in all_menu_items if item.id in allowed_ids]
        
        # If no user or no access level, menu_items remains [] (or maybe we allow public items?)
        # For this system, assume strictly authenticated.

        
        # Clear existing menu items
        for widget in self.menu_container.winfo_children():
            widget.destroy()

        # Group child menus by parent_id
        children_map = {}
        for item in menu_items:
            if item.parent_id:
                children_map.setdefault(item.parent_id, []).append(item)

        for item in menu_items:
            if item.navigation_type == "menu":
                self.render_menu(item)

            elif item.navigation_type == "parent_menu":
                self.render_parent_menu(item, children_map.get(item.id, []))

    # --------------------------------------------------
    # Renderers
    # --------------------------------------------------
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
