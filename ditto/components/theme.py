from tkinter import ttk

LIGHT_THEME = {
    "root_bg": "#f6f1fb",
    "card_bg": "#ffffff",
    "border": "#e7d9f7",
    "text": "#2d2238",
    "muted": "#6f617d",
    "accent": "#efe5fb",
    "button": "#d9c9f3",
    "button_active": "#cdb7ee",
    "footer": "#9a8cab"
}

DARK_THEME = {
    "root_bg": "#1c1824",
    "card_bg": "#2a2435",
    "border": "#433a54",
    "text": "#f3ecff",
    "muted": "#c5b7dc",
    "accent": "#3a3247",
    "button": "#4a3f5e",
    "button_active": "#5c4e74",
    "footer": "#a99bbb"
}

def setup_style(root):
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except:
        pass

    root.configure(bg="#f6f1fb")

    style.configure(
        "Custom.TButton",
        font=("Arial", 11, "bold"),
        padding=10,
        background=root.theme["button"],
        foreground=root.theme["text"],
        borderwidth=0,
        relief="flat",
        focusthickness=0,
        focuscolor=root.theme["button"],
        lightcolor=root.theme["button"],
        darkcolor=root.theme["button"],
        highlightthickness=0
    )    

    style.map(
        "Custom.TButton",
        background=[
            ("active", root.theme["button_active"]),
            ("pressed", root.theme["button_active"]),
            ("!disabled", root.theme["button"])
        ],
        foreground=[
            ("active", root.theme["text"]),
            ("pressed", root.theme["text"]),
            ("!disabled", root.theme["text"])
        ],
        lightcolor=[("!disabled", root.theme["button"])],
        darkcolor=[("!disabled", root.theme["button"])],
        bordercolor=[("!disabled", root.theme["button"])],
        focuscolor=[("!disabled", root.theme["button"])]
    )

    style.configure("TEntry", padding=6)
    style.configure("TCombobox", padding=5)
    style.configure(
        "TRadiobutton",
        background=root.theme["card_bg"],
        foreground=root.theme["text"],
        font=("Arial", 10)
    )