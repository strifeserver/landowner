from tkinter import ttk

def apply_treeview_style():
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Custom.Treeview",
        background="white",
        foreground="black",
        rowheight=25,
        fieldbackground="white",
        bordercolor="black",
        borderwidth=1,
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", "#e1e5f2")],
        foreground=[("selected", "black")],
    )
    style.configure(
        "Custom.Treeview.Heading",
        background="black",
        foreground="white",
        font=("Arial", 10, "bold"),
        borderwidth=1,
    )
    style.layout(
        "Custom.Treeview",
        [
            (
                "Treeview.field",
                {
                    "sticky": "nswe",
                    "border": "1",
                    "children": [
                        (
                            "Treeview.padding",
                            {
                                "sticky": "nswe",
                                "children": [
                                    ("Treeview.treearea", {"sticky": "nswe"})
                                ],
                            },
                        )
                    ],
                },
            )
        ],
    )
