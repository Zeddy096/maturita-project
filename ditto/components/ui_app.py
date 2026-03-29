import tkinter as tk
from tkinter import ttk

from components.ui_main_menu import MainMenu
from components.ui_search_page import SearchPage
from components.ui_db_page import DatabasePage
from components.ui_recipe_page import RecipePage
from components.theme import LIGHT_THEME, DARK_THEME, setup_style
from components.settings import load_config, save_config


class DittoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ditto")
        width = 1000
        height = 750
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(800, 600)

        self.config_data = load_config()

        if self.config_data.get("theme") == "dark":
            self.theme = DARK_THEME
        else:
            self.theme = LIGHT_THEME

        setup_style(self)

        container = tk.Frame(self, bg=self.theme["root_bg"])
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.container = container
        self.frames = {}

        for F in (MainMenu, SearchPage, DatabasePage, RecipePage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")
        self.apply_theme()

    def apply_theme(self):
        self.configure(bg=self.theme["root_bg"])
        self.container.configure(bg=self.theme["root_bg"])

        setup_style(self)

        for frame in self.frames.values():
            if hasattr(frame, "apply_theme"):
                frame.apply_theme()

    def toggle_theme(self):
        if self.theme == LIGHT_THEME:
            self.theme = DARK_THEME
            self.config_data["theme"] = "dark"
        else:
            self.theme = LIGHT_THEME
            self.config_data["theme"] = "light"
        
        save_config(self.config_data)

        self.apply_theme()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "DatabasePage":
            frame.refresh()
        if page_name == "SearchPage":
            frame.refresh_all()            
        frame.tkraise()