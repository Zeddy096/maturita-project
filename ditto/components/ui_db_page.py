import tkinter as tk
from tkinter import ttk, messagebox

from database import get_recept, get_recepty, delete_recept
from components.ui_add_recipe_page import AddRecipeWindow
from components.theme import DARK_THEME

class DatabasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.theme["root_bg"])
        self.controller = controller
        t = controller.theme
        self.ids = []

        # main card
        self.card = tk.Frame(
            self,
            bg=t["card_bg"],
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.card.pack(fill="both", expand=True, padx=20, pady=20)

        # top frame
        self.top_frame = tk.Frame(self.card, bg=t["card_bg"])
        self.top_frame.pack(fill="x", padx=20, pady=(18, 8))

        self.title_wrap = tk.Frame(self.top_frame, bg=t["card_bg"])
        self.title_wrap.pack(side="left")

        self.title_label = tk.Label(
            self.title_wrap,
            text="Databáze receptů",
            font=("Arial", 22, "bold"),
            bg=t["card_bg"],
            fg=t["text"]
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            self.title_wrap,
            text="Spravuj svoje uložené recepty",
            font=("Arial", 10),
            bg=t["card_bg"],
            fg=t["muted"]
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # recipe list + scrollbar
        list_frame = tk.Frame(self.card, bg=t["card_bg"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=14)

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

        # bottom buttons
        self.btn_frame = tk.Frame(self.card, bg=t["card_bg"])
        self.btn_frame.pack(pady=(0, 20))

        self.add_btn = tk.Button(
            self.btn_frame,
            text="Přidat recept",
            command=self.open_add_window,
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
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.add_btn.pack(side="left", padx=5)

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
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.show_btn.pack(side="left", padx=5)

        self.edit_btn = tk.Button(
            self.btn_frame,
            text="Upravit",
            command=self.edit_selected,
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
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.edit_btn.pack(side="left", padx=5)       

        self.delete_btn = tk.Button(
            self.btn_frame,
            text="Smazat",
            command=self.delete_selected,
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
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.delete_btn.pack(side="left", padx=5)

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
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.back_btn.pack(side="left", padx=5)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.ids = []

        for i, (rid, nazev, cas_min) in enumerate(get_recepty(), start=1):
            cas_text = f"{cas_min} min" if cas_min is not None else "-"
            self.listbox.insert(tk.END, f"{i}. {nazev} ({cas_text})")
            self.ids.append(rid)

    def _get_selected_id(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Nejprve vyber recept.")
            return None
        
        index = sel[0]
        if index < 0 or index >= len(self.ids):
            return None
        
        return self.ids[index] 
                
    def open_add_window(self):
        AddRecipeWindow(self, on_saved=self.refresh)

    def open_recept(self):
        rid = self._get_selected_id()
        if rid is None:
            return
        
        recipe_page = self.controller.frames["RecipePage"]
        recipe_page.back_target = "DatabasePage"           
        recipe_page.set_recept(rid)
        self.controller.show_frame("RecipePage")

    def edit_selected(self):    
        rid = self._get_selected_id()
        if rid is None:
            return
        
        data = get_recept(rid)
        if data is None:
            return
        
        rid_db, nazev, cas, suroviny, postup, cas_min, image_path, tags = data

        win = AddRecipeWindow(
            self,
            on_saved=self.refresh,
            data=(nazev, cas_min, suroviny, postup, image_path, tags)
        )
        win.set_id(rid)

    def delete_selected(self):
        rid = self._get_selected_id()
        if rid is None:
            return
        
        if messagebox.askyesno("Smazat", "Opravdu chceš smazat tenhle recept?"):
            delete_recept(rid)
            self.refresh()

    def apply_theme(self):

        t = self.controller.theme

        self.configure(bg=t["root_bg"])
        self.card.configure(bg=t["card_bg"], highlightbackground=t["border"])
        self.top_frame.configure(bg=t["card_bg"])
        self.btn_frame.configure(bg=t["card_bg"])

        self.title_label.configure(bg=t["card_bg"], fg=t["text"])
        self.subtitle_label.configure(bg=t["card_bg"], fg=t["muted"])

        self.title_wrap.configure(bg=t["card_bg"])

        self.listbox.configure(
            bg=t["card_bg"],
            fg=t["text"],
            selectbackground="#5a4a7c" if self.controller.theme == DARK_THEME else "#bfa8ea",
            selectforeground=t["text"]    
        )

        for btn in (self.add_btn, self.show_btn, self.edit_btn, self.delete_btn, self.back_btn):
            btn.configure(
                bg=t["button"],
                fg=t["text"],
                activebackground=t["button_active"],
                activeforeground=t["text"],
                highlightbackground=t["button"],
                highlightcolor=t["button"]
            )