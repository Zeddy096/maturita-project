import tkinter as tk
from tkinter import ttk, messagebox

from database import get_recepty, search_recepty
from components.theme import DARK_THEME


class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.theme["root_bg"])
        self.controller = controller
        t = controller.theme
        self.ids = []

        # main card
        self.card = tk.Frame(
            self,
            bg=t["card_bg"],
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.card.pack(fill="both", expand=True, padx=20, pady=20)
 
        # title
        self.title_label = tk.Label(
            self.card,
            text="Vyhledávání receptů",
            font=("Arial", 20, "bold"),
            bg=t["card_bg"],
            fg=t["text"]
        )
        self.title_label.pack(pady=12)

        # top row
        self.top = tk.Frame(self.card, bg=t["card_bg"])
        self.top.pack(pady=5)

        self.search_label = tk.Label(
            self.top,
            text="Hledat:",
            bg=t["card_bg"],
            fg=t["text"]
        )
        self.search_label.pack(side="left", padx=5)

        self.entry = ttk.Entry(self.top, width=20)
        self.entry.pack(side="left", padx=5)
        self.entry.bind("<Return>", lambda e: self.do_search())

        self.combo = ttk.Combobox(self.top, state="readonly", width=12)
        self.combo["values"] = ("Název", "Čas", "Suroviny", "Štítky")
        self.combo.current(0)
        self.combo.pack(side="left", padx=5)

        self.time_cmp = tk.StringVar(master=self, value="le")

        # time filter
        self.time_frame = tk.Frame(self.top, bg=t["card_bg"])

        self.rb_le = ttk.Radiobutton(
            self.time_frame,
            text="≤",
            value="le",
            variable=self.time_cmp
        )

        self.rb_eq = ttk.Radiobutton(
            self.time_frame,
            text="=",
            value="eq",
            variable=self.time_cmp
        )

        self.rb_le.pack(side="left", padx=2)
        self.rb_eq.pack(side="left", padx=2)

        self.combo.bind("<<ComboboxSelected>>", lambda e: self._toggle_time_cmp())
        self._toggle_time_cmp()

        self.search_btn = tk.Button(
            self.top,
            text="Hledat",
            command=self.do_search,
            font=("Arial", 11, "bold"),
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=t["button"],
            padx=18,
            pady=8,
            cursor="hand2"
        )
        self.search_btn.pack(side="left", padx=6)
        
        # listbox + scrollbar
        list_frame = tk.Frame(self.card, bg=self.controller.theme["card_bg"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=12)

        self.listbox = tk.Listbox(
            list_frame,
            bg=t["card_bg"],
            fg=t["text"],
            selectbackground="#5a4a7c" if self.controller.theme == DARK_THEME else "#bfa8ea",
            selectforeground=self.controller.theme["text"],
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
            font=("Arial", 11)
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_recept())

        self.scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.listbox.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        # buttons
        self.btn_frame = tk.Frame(self.card, bg=t["card_bg"])
        self.btn_frame.pack(pady=10)

        self.show_btn = tk.Button(
            self.btn_frame,
            text="Zobrazit",
            command=self.open_recept,
            font=("Arial", 11, "bold"),
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=t["button"],
            highlightcolor=t["button"],
            padx=30,
            pady=20,
            cursor="hand2"
        )
        self.show_btn.pack(side="left", padx=5)

        self.back_btn = tk.Button(
            self.btn_frame,
            text="Zpět",
            command=lambda: controller.show_frame("MainMenu"),
            font=("Arial", 11, "bold"),
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=t["button"],
            highlightcolor=t["button"],
            padx=30,
            pady=20,
            cursor="hand2"
        )
        self.back_btn.pack(side="left", padx=5)

    def refresh_all(self):
        self.listbox.delete(0, tk.END)
        self.ids = []

        for i, (rid, nazev, cas_min) in enumerate(get_recepty(), start=1):
            cas_text = f"{cas_min} min" if cas_min is not None else "-"
            self.listbox.insert(tk.END, f"{i}. {nazev} ({cas_text})")
            self.ids.append(rid)

    def do_search(self):
        text = self.entry.get().strip()

        if not text:
            self.refresh_all()
            return

        mode_label = self.combo.get()

        if mode_label == "Čas":
            if not text.isdigit():
                messagebox.showinfo("Info", "U času zadej jen číslo v minutách.")
                return
            rows = search_recepty(text, mode="cas", time_cmp=self.time_cmp.get())
        elif mode_label == "Suroviny":
            rows = search_recepty(text, mode="suroviny")
        elif mode_label == "Štítky":
            rows = search_recepty(text, mode="tags")
        else:
            rows = search_recepty(text, mode="nazev")

        if rows is None:
            rows = []

        self.listbox.delete(0, tk.END)
        self.ids = []

        for i, (rid, nazev, cas_min) in enumerate(rows, start=1):
            cas_text = f"{cas_min} min" if cas_min is not None else "-"
            self.listbox.insert(tk.END, f"{i}. {nazev} ({cas_text})")
            self.ids.append(rid)

    def _toggle_time_cmp(self):
        if self.combo.get() == "Čas":
            self.time_frame.pack(side="left", padx=5)
        else:
            self.time_frame.pack_forget()

    def _get_selected_id(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Nejprve vyber recept.")
            return None
        return self.ids[sel[0]]            

    def open_recept(self):
        rid = self._get_selected_id()
        if rid is None:
            return
        
        recipe_page = self.controller.frames["RecipePage"]
        recipe_page.back_target = "SearchPage"
        recipe_page.set_recept(rid)
        self.controller.show_frame("RecipePage")                                                                                            

    def apply_theme(self):
        t = self.controller.theme

        self.configure(bg=t["root_bg"])
        self.card.configure(bg=t["card_bg"], highlightbackground=t["border"])
        self.top.configure(bg=t["card_bg"])
        self.btn_frame.configure(bg=t["card_bg"])

        self.title_label.configure(bg=t["card_bg"], fg=t["text"])
        self.search_label.configure(bg=t["card_bg"], fg=t["text"])
        self.time_frame.configure(bg=t["card_bg"])

        self.listbox.configure(
            bg=t["card_bg"],
            fg=t["text"],
            selectbackground="#5a4a7c" if self.controller.theme == DARK_THEME else "#bfa8ea",
            selectforeground=t["text"]
        )

        self.search_btn.configure(
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            highlightbackground=t["button"],
            highlightcolor=t["button"]
        )

        self.show_btn.configure(
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            highlightbackground=t["button"],
            highlightcolor=t["button"]
        )

        self.back_btn.configure(
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            highlightbackground=t["button"],
            highlightcolor=t["button"]
        )