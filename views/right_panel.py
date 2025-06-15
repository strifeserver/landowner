#right_panel.py
import tkinter as tk
from tkinter import ttk
from views.table_view import TableView
import importlib
from utils.debug import print_r

class RightPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#ffffff", *args, **kwargs)
        self.pack_propagate(False)
        self.render_default()

    def render_default(self):
        self.clear()
        tk.Label(
            self, text="Welcome to the Right Panel", bg="#ffffff", font=("Arial", 12)
        ).pack(pady=20)

    def render_content(self, nav_name, ctrlName, navigation_name):
        self.clear()

        try:
            controller_name = f"{nav_name}_controller"
            controller_module = importlib.import_module(
                f"controllers.{controller_name}"
            )
            controller_class = getattr(controller_module, ctrlName)

            # Fetch initial result (e.g., page 1)
            result = controller_class.index(
                filters={}, pagination=True, items_per_page=10, page=1
            )

            if result:
                model_class = result[0].__class__
                # Get visible fields and labels using model method
                visible_fields = model_class.get_visible_fields()
                columns = [field for field, _ in visible_fields]
                column_labels = [alias for _, alias in visible_fields]
                data = [obj.__dict__ for obj in result]

                def controller_callback(filters=None, searchAll=None):
                    try:
                        filtered = controller_class.index(
                            filters=filters,
                            pagination=True,
                            items_per_page=10,
                            page=1,
                            searchAll=searchAll,
                        )
                        return [obj.__dict__ for obj in filtered]
                    except Exception as err:
                        print("Filter error:", err)
                        return []

                table = TableView(
                    self,
                    columns=columns,
                    column_labels=column_labels,
                    data=data,
                    controller_callback=controller_callback,
                    title=navigation_name,
                )
                table.pack(fill=tk.BOTH, expand=True)

            else:
                tk.Label(self, text="No data found", bg="#ffffff").pack(pady=20)

        except Exception as e:
            tk.Label(
                self, text=f"Error loading: {str(e)}", fg="red", bg="#ffffff"
            ).pack(pady=20)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
