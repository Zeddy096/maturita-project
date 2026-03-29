import os
import tkinter as tk
from tkinter import ttk

from components.theme import DARK_THEME

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f6f1fb")
        self.controller = controller
        t = controller.theme

        # main card
        self.card = tk.Frame(
            self,
            bg=t["card_bg"],
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=500)

        # dark mode toggle
        self.top_bar = tk.Frame(self.card, bg=t["card_bg"])
        self.top_bar.pack(fill="x", padx=18, pady=(14, 0))

        self.toggle_btn = ttk.Button(
            self.top_bar,
            text="Light mode",
            style="Custom.TButton",
            command=self.controller.toggle_theme
        )
        self.toggle_btn.pack(side="right")

        if self.controller.theme == DARK_THEME:
            self.toggle_btn.configure(text="Light mode")
        else:
            self.toggle_btn.configure(text="Dark mode")

        # title
        self.title_label = tk.Label(
            self.card,
            text="Ditto",
            font=("Arial", 30, "bold"),
            bg=t["card_bg"],
            fg=t["text"]
        )
        self.title_label.pack(pady=(18, 8))

        self.subtitle_label = tk.Label(
            self.card,
            text="Tvoje kuchařka receptů",
            font=("Arial", 12),
            bg=t["card_bg"],
            fg=t["muted"],
        )
        self.subtitle_label.pack(pady=(0, 18))

        # ditto image
        self.img_wrap = tk.Frame(self.card, bg=t["card_bg"])
        self.img_wrap.pack(pady=10)

        if  HAS_PIL and os.path.exists("ditto.jpg"):
            self.pil_img = Image.open("ditto.jpg")
            self.pil_img.thumbnail((210, 210))

            self.img = ImageTk.PhotoImage(self.pil_img)

            self.img_label = tk.Label(
                self.img_wrap,
                image=self.img,
                bg=controller.theme["card_bg"]
            )
            self.img_label.pack()
        else:
            self.img_label = tk.Label(
                self.img_wrap,
                text="[Chybí obrázek Ditto]",
                font=("Arial", 11),
                bg=t["card_bg"],
                fg=t["muted"]
            )
            self.img_label.pack(pady=40)

        # separator
        self.separator = tk.Frame(self.card, bg=t["accent"], height=1)
        self.separator.pack(fill="x", padx=60, pady=18)

        # buttons
        self.btn_wrap = tk.Frame(self.card, bg=t["card_bg"])
        self.btn_wrap.pack(fill="x", padx=70, pady=(10, 6))

        self.search_btn = ttk.Button(
            self.btn_wrap,
            text="Vyhledávání",
            command=lambda: controller.show_frame("SearchPage"),
            style="Custom.TButton"
        )
        self.search_btn.pack(fill="x", pady=8, ipady=6)
    
        self.db_btn = ttk.Button(
            self.btn_wrap,
            text="Databáze receptů",
            command=lambda: controller.show_frame("DatabasePage"),
            style="Custom.TButton"
        )
        self.db_btn.pack(fill="x", pady=8, ipady=6)
    
        self.quit_btn = ttk.Button(
            self.btn_wrap,
            text="Ukončit",
            command=controller.quit,
            style="Custom.TButton"
        )
        self.quit_btn.pack(fill="x", pady=8, ipady=6)

        # footer text
        self.footer_wrap = tk.Frame(self.card, bg=controller.theme["card_bg"])
        self.footer_wrap.pack(side="bottom", fill="x", pady=(8, 18))

        self.footer_label = tk.Label(
            self.footer_wrap,
            text="Ditto Desktop v1.0",
            font=("Arial", 9),
            bg=t["card_bg"],
            fg=t["footer"]
        )
        self.footer_label.pack()

    def apply_theme(self):
        t = self.controller.theme

        self.configure(bg=t["root_bg"])

        self.card.configure(bg=t["card_bg"], highlightbackground=t["border"])
        self.top_bar.configure(bg=t["card_bg"])
        self.img_wrap.configure(bg=t["card_bg"])
        self.btn_wrap.configure(bg=t["card_bg"])
        self.footer_wrap.configure(bg=t["card_bg"])

        self.title_label.configure(bg=t["card_bg"], fg=t["text"])
        self.subtitle_label.configure(bg=t["card_bg"], fg=t["muted"])
        self.img_label.configure(bg=t["card_bg"])
        self.separator.configure(bg=t["accent"])
        self.footer_label.configure(bg=t["card_bg"], fg=t["footer"])

        if self.controller.theme == DARK_THEME:
            self.toggle_btn.configure(text="Light mode")
        else:
            self.toggle_btn.configure(text="Dark mode")