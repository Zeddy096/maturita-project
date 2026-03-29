import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from database import add_recept, update_recept, save_image_for_recipe
from components.utils import bind_scroll_recursive

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class AddRecipeWindow(tk.Toplevel):
    def __init__(self, parent, on_saved=None, data=None):
        super().__init__(parent)
        self.controller = parent.controller
        self.on_saved = on_saved
        self.recept_id = None
        self.image_path = None
        self.old_image_path = None
        self._preview_ref = None

        t = self.controller.theme

        self.title("Přidat recept" if data is None else "Upravit recept")
        self.geometry("600x700")
        self.minsize(500, 500)
        self.configure(bg=t["root_bg"])

        # canvas + scrollbar
        self.canvas = tk.Canvas(self, bg=t["root_bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # inner frame
        self.scroll_frame = tk.Frame(self.canvas, bg=t["root_bg"])
        self.window_id = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.window_id, width=e.width)
        )

        # main card
        self.card = tk.Frame(
            self.scroll_frame,
            bg=t["card_bg"],
            highlightthickness=1,
            highlightbackground=t["border"]
        )      
        self.card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # title
        tk.Label(
            self.card,
            text="Název:",
            bg=t["card_bg"],
            fg=t["text"],
            font=("Arial", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 2))

        self.name_entry = tk.Entry(
            self.card,
            bg=t["card_bg"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.name_entry.pack(fill="x", padx=12, pady=4)

        # time
        tk.Label(
            self.card,
            text="Čas (v minutách):",
            bg=t["card_bg"],
            fg=t["text"],
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))
        
        self.time_entry = tk.Entry(
            self.card,
            bg=t["card_bg"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.time_entry.pack(fill="x", padx=12, pady=4)
        
        # ingrediemts
        tk.Label(
            self.card,
            text="Suroviny:",
            bg=t["card_bg"],
            fg=t["text"],
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))

        self.ing_text = tk.Text(
            self.card,
            height=8,
            wrap="word",
            bg=t["card_bg"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.ing_text.pack(fill="both", padx=12, pady=4)

        # procedure
        tk.Label(
            self.card,
            text="Postup:",
            bg=t["card_bg"],
            fg=t["text"],
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))

        self.proc_text = tk.Text(
            self.card,
            height=8,
            wrap="word",
            bg=t["card_bg"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.proc_text.pack(fill="both", padx=12, pady=4)

        # tags
        tk.Label(
            self.card,
            text="Štítky (oddělené čárkou):",
            bg=t["card_bg"],
            fg=t["text"],
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))

        self.tags_entry = tk.Entry(
            self.card,
            bg=t["card_bg"],
            fg=t["text"],
            insertbackground=t["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.tags_entry.pack(fill="x", padx=12, pady=4)

        # image
        self.img_label = tk.Label(
            self.card,
            text="Obrázek: žádný",
            bg=t["card_bg"],
            fg=t["muted"],
        )
        self.img_label.pack(pady=8)

        self.img_btn = tk.Button(
            self.card,
            text="Vybrat obrázek",
            command=self.choose_image,
            font=("Arial", 10, "bold"),
            bg=t["button"],
            fg=t["text"],
            relief="flat",
            bd=0,
            activebackground=t["button_active"],
            activeforeground=t["text"],
            highlightthickness=0,
            highlightbackground=t["button"],
            highlightcolor=t["button"],
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.img_btn.pack()
        self.preview_label = tk.Label(
            self.card,
            bg=t["card_bg"],
            fg=t["muted"],
            text=""
        )
        self.preview_label.pack(pady=(10, 6))

        # buttons
        self.btn_frame = tk.Frame(self.card, bg=t["card_bg"])
        self.btn_frame.pack(pady=14)

        self.save_btn = tk.Button(
            self.btn_frame,
            text="Uložit",
            command=self.save,
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
        self.save_btn.pack(side="left", padx=5)

        self.cancel_btn = tk.Button(
            self.btn_frame,
            text="Zrušit",
            command=self.destroy,
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
        self.cancel_btn.pack(side="left", padx=5)

        if data:
            nazev, cas_min, suroviny, postup, image_path, tags = data
            self.name_entry.insert(0, nazev)
            self.time_entry.insert(0, "" if cas_min is None else str(cas_min))
            self.ing_text.insert("1.0", suroviny)
            self.proc_text.insert("1.0", postup)
            self.tags_entry.insert(0, tags or "")

            if image_path:
                self.image_path = image_path
                self.old_image_path = image_path
                self.img_label.config(text=os.path.basename(image_path))
                self.update_preview(image_path)

        # modal behavior
        self.grab_set()
        self.name_entry.focus()

        # mousewheel scrolling
        bind_scroll_recursive(self, self.canvas)

    def set_id(self, rid):
        self.recept_id = rid
        self.title("Upravit recept")
  
    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Vyber obrázek",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.gif"), ("All files", "*.*")]
            )
        if path:
            self.image_path = path
            self.img_label.config(text=os.path.basename(path))
            self.update_preview(path)

    def update_preview(self, path):
        t = self.controller.theme

        if path and os.path.exists(path) and HAS_PIL:
            try:
                img = Image.open(path)
                img.thumbnail((180, 180))
                self._preview_ref = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self._preview_ref, text="", bg=t["card_bg"])
            except Exception:
                self._preview_ref = None
                self.preview_label.config(image="", text="Náhled nejde načíst", fg=t["muted"], bg=t["card_bg"])
        else:
            self._preview_ref = None
            self.preview_label.config(image="", text="", bg=t["card_bg"])

    def save(self):
        nazev = self.name_entry.get().strip()
        cas = self.time_entry.get().strip()
        suroviny = self.ing_text.get("1.0", "end").strip()
        postup = self.proc_text.get("1.0", "end").strip()
        tags = ", ".join([t.strip().lower() for t in self.tags_entry.get().split(",") if t.strip()])

        if not nazev:
            messagebox.showwarning("Chyba", "Název je povinný.")
            return
        
        if cas != "":
            try:
                cas_val = int(cas)
            except ValueError:
                messagebox.showwarning("Chyba", "Čas musí být číslo.")
                return
            
            if cas_val < 0:
                messagebox.showwarning("Chyba", "Čas nemůže být záporný.")
                return
            
            if cas_val > 10000:
                messagebox.showwarning("Chyba", "Čas je příliš vysoký.")
                return
        else:
            cas_val = None
            
        if len(nazev) > 200:
            messagebox.showwarning("Chyba", "Název je příliš dlouhý.")
            return
        
        if len(suroviny) > 5000:
            messagebox.showwarning("Chyba", "Seznam surovin je příliš dlouhý.")
            return
        
        if len(postup) > 20000:
            messagebox.showwarning("Chyba", "Postup je příliš dlouhý.")
            return

        if self.recept_id is None:
            rid = add_recept(nazev, cas_val, suroviny, postup, image_path=None, tags=tags)

            img_final = None
            if self.image_path:
                img_final = save_image_for_recipe(rid, self.image_path)
            
            update_recept(rid, nazev, cas_val, suroviny, postup, image_path=img_final, tags=tags)  

        else:
            if self.image_path:
                img_final = save_image_for_recipe(self.recept_id, self.image_path)
            else:
                img_final = self.old_image_path
            
            update_recept(self.recept_id, nazev, cas_val, suroviny, postup, image_path=img_final, tags=tags)     
        
        if self.on_saved:
            self.on_saved()

        self.destroy()