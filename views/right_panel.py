# views/right_panel.py
import tkinter as tk
from views.table_view import TableView
import importlib

class RightPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#ffffff", *args, **kwargs)
        self.pack_propagate(False)
        self.render_default()

    def render_default(self):
        self.clear()
        tk.Label(self, text="Welcome to the Right Panel", bg="#ffffff", font=("Arial", 12)).pack(pady=20)

    def render_content(self, nav_name, ctrlName):
        self.clear()

        try:
            controller_name = f"{nav_name}_controller"
            controller_module = importlib.import_module(f"controllers.{controller_name}")
            controller_class = getattr(controller_module, ctrlName)

            # Default fetch (page 1, no filters)
            result = controller_class.index(
                filters={},
                pagination=True,
                items_per_page=5,
                page=1
            )

            if result:
                columns = list(result[0].__dict__.keys())
                data = [obj.__dict__ for obj in result]

                def controller_callback(filters=None, searchAll=None):
                    try:
                        filtered = controller_class.index(
                            filters=filters,
                            pagination=True,
                            items_per_page=5,
                            page=1,
                            searchAll=searchAll
                        )
                        return [obj.__dict__ for obj in filtered]
                    except Exception as err:
                        print("Filter error:", err)
                        return []

                table = TableView(
                    self,
                    columns=columns,
                    data=data,
                    controller_callback=controller_callback,
                    title=nav_name.replace("_", " ").title()
                )
                table.pack(fill=tk.BOTH, expand=True)
            else:
                tk.Label(self, text="No data found", bg="#ffffff").pack(pady=20)

        except Exception as e:
            tk.Label(self, text=f"Error loading: {str(e)}", fg="red", bg="#ffffff").pack(pady=20)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
