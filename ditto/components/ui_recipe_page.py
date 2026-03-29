import os
import tkinter as tk
from tkinter import ttk

from database import get_recept
from components.utils import bind_scroll_recursive

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False



class RecipePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.theme["root_bg"])
        self.controller = controller
        t = controller.theme
        self._img_ref = None
        self.back_target = "DatabasePage"

        # canvas + scrollbar
        self.canvas = tk.Canvas(self, bg=t["root_bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # inner frame
        self.scroll_frame = tk.Frame(self.canvas, bg=t["root_bg"])
        self.window_id = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # scroll region
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # expanding width of content
        self.canvas.bind("<Configure>", self._resize_frame)

        # main card
        self.card = tk.Frame(
            self.scroll_frame,
            bg=t["card_bg"],
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.card.pack(fill="both", expand=True, padx=24, pady=24)

        # top bar
        self.top = tk.Frame(self.card, bg=t["card_bg"])
        self.top.pack(fill="x", padx=20, pady=(18, 8))
        
        self.back_btn = tk.Button(
            self.top,
            text="Zpět",
            command=self.go_back,
            font=("Arial", 11, "bold"),
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            bd=0,
            highlightthickness=0,
            highlightbackground=t["button"],
            highlightcolor=t["button"],
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.back_btn.pack(side="left")

        self.title_label = tk.Label(
            self.card,
            text="",
            font=("Arial", 24, "bold"),
            bg=t["card_bg"],
            fg=t["text"],
            wraplength=700,
            justify="center"
        )
        self.title_label.pack(padx=20, pady=(10, 8))

        self.img_label = tk.Label(
            self.card,
            bg=t["card_bg"],
            fg=t["muted"]
        )
        self.img_label.pack(pady=10)

        self.info_label = tk.Label(
            self.card,
            text="",
            font=("Arial", 11, "bold"),
            bg=t["card_bg"],
            fg=t["muted"]
        )
        self.info_label.pack(pady=5)

        self.tags_label = tk.Label(
            self.card,
            text="",
            font=("Arial", 10, "bold"),
            bg=t["card_bg"],
            fg=t["muted"],
            wraplength=700,
            justify="center"
        )
        self.tags_label.pack(padx=20, pady=(0, 10))

        # ingredients section
        self.ing_card = tk.Frame(
            self.card,
            bg=t["accent"],
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.ing_card.pack(fill="x", padx=24, pady=12)

        self.ing_title = tk.Label(
            self.ing_card,
            text="Suroviny",
            font=("Arial", 13, "bold"),
            bg=t["accent"],
            fg=t["text"],
        )
        self.ing_title.pack(anchor="w", padx=14, pady=(12, 6))

        self.ing_text = tk.Text(
            self.ing_card,
            height=1,
            font=("Arial", 11),
            bd=0,
            wrap="word",
            bg=t["accent"],
            fg=t["text"],
            highlightthickness=0,
            relief="flat",
            padx=4,
            pady=4,
            spacing1=1,
            spacing3=1
        )
        self.ing_text.pack(fill="x", padx=14, pady=(0, 14))
        self.ing_text.config(state="disabled", cursor="arrow")

        # procedure section
        self.proc_card = tk.Frame(
            self.card,
            bg=t["accent"],
            highlightthickness=1,
            highlightbackground=t["border"]
        )
        self.proc_card.pack(fill="x", padx=24, pady=12)

        self.proc_title = tk.Label(
            self.proc_card,
            text="Postup",
            font=("Arial", 13, "bold"),
            bg=t["accent"],
            fg=t["text"]
        )
        self.proc_title.pack(anchor="w", padx=14, pady=(12, 6))
        
        self.proc_text = tk.Text(
            self.proc_card,
            height=1,
            font=("Arial", 11),
            bd=0,
            wrap="word",
            bg=t["accent"],
            fg=t["text"],
            highlightthickness=0,
            relief="flat",
            padx=4,
            pady=4,
            spacing1=1,
            spacing3=1
        )
        self.proc_text.pack(fill="x", padx=14, pady=(0, 14))
        self.proc_text.config(state="disabled", cursor="arrow")

        # mousewheel scrolling
        bind_scroll_recursive(self, self.canvas)

        # stop scrolling inside text widgets
        self.ing_text.bind("<MouseWheel>", self._text_mousewheel)
        self.ing_text.bind("<Button-4>", self._text_mousewheel)
        self.ing_text.bind("<Button-5>", self._text_mousewheel)

        self.proc_text.bind("<MouseWheel>", self._text_mousewheel)
        self.proc_text.bind("<Button-4>", self._text_mousewheel)
        self.proc_text.bind("<Button-5>", self._text_mousewheel)

    def go_back(self):
        self.controller.show_frame(self.back_target)
        
    def _resize_frame(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

        # dynamic title wrapping
        self.title_label.config(wraplength=max(300, event.width - 100))

    def _fit_title(self, text):
        base_size = 24
        min_size = 16

        length = len(text)

        if length < 30:
            size = base_size
        elif length < 60:
            size = 20
        elif length < 100:
            size = 18
        else:
            size = min_size

        self.title_label.config(font=("Arial", size, "bold"))

    def _text_mousewheel(self, event):
        if hasattr(event, "num"):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
                return "break"
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
                return "break"
            
        if hasattr(event, "delta") and event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"            

    def _fit_text_height(self, widget):

        # sets text widgets height by the real number of shown lines
        try:
            lines = int(widget.count("1.0", "end", "displaylines")[0])
        except Exception:
            content = widget.get("1.0", "end-1c")
            lines = max(1, len(content.splitlines()))

        widget.config(height=max(1, lines))

    def _set_text(self, widget, value):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        self._fit_text_height(widget)
        widget.config(state="disabled")

    def set_recept(self, rid):
        data = get_recept(rid)
        if data is None:
            self.title_label.config(text="Recept nenalezen")
            self.info_label.config(text="")
            self.tags_label.config(text="")
            self._set_text(self.ing_text, "")
            self._set_text(self.proc_text, "")
            self.img_label.config(image="", text="")
            self._img_ref = None
            return

        rid_db, nazev, cas, suroviny, postup, *rest = data
        cas_min = rest[0] if len(rest) > 0 else None
        image_path = rest[1] if len(rest) > 1 else None
        tags = rest[2] if len(rest) > 2 else ""

        self.title_label.config(text=nazev)
        self._fit_title(nazev)

        if cas_min is None or cas_min == "":
            self.info_label.config(text="Čas: -")
        else:
            self.info_label.config(text=f"Čas: {cas_min} min")

        if tags and tags.strip():
            pretty_tags = ", ".join(tag.strip() for tag in tags.split(",") if tag.strip())
            self.tags_label.config(text=f"Štítky: {pretty_tags}")
        else:
            self.tags_label.config(text="Štítky: žádné")

        self._set_text(self.ing_text, suroviny if suroviny else "-")
        self._set_text(self.proc_text, postup if postup else "-")
        
        self._img_ref = None
        self.img_label.config(image="", text="")
        
        if image_path and os.path.exists(image_path) and HAS_PIL:
            try:
                img = Image.open(image_path)
                img.thumbnail((320, 320))
                self._img_ref = ImageTk.PhotoImage(img)
                self.img_label.config(image=self._img_ref)
            except Exception:
                self.img_label.config(text="Obrázek nejde načíst:", fg="#6f617d")
        elif image_path and os.path.exists(image_path):
            self.img_label.config(text=f"Obrázek: {os.path.basename(image_path)}", fg="#6f617d")
        else:
            self.img_label.config(text="Obrázek: žádný", fg="#6f617d")

        # moves up after opening recipe
        self.canvas.yview_moveto(0)
    
    def apply_theme(self):

        t = self.controller.theme

        self.configure(bg=t["root_bg"])
        self.canvas.configure(bg=t["root_bg"])
        self.scroll_frame.configure(bg=t["root_bg"])

        self.card.configure(bg=t["card_bg"], highlightbackground=t["border"])
        self.top.configure(bg=t["card_bg"])

        self.back_btn.configure(
            bg=t["button"],
            fg=t["text"],
            activebackground=t["button_active"],
            activeforeground=t["text"],
            highlightbackground=t["button"],
            highlightcolor=t["button"]
        )

        self.title_label.configure(bg=t["card_bg"], fg=t["text"])
        self.img_label.configure(bg=t["card_bg"], fg=t["muted"])
        self.info_label.configure(bg=t["card_bg"], fg=t["muted"])
        self.tags_label.configure(bg=t["card_bg"], fg=t["muted"])

        self.ing_card.configure(bg=t["accent"], highlightbackground=t["border"])
        self.ing_title.configure(bg=t["accent"], fg=t["text"])
        self.ing_text.configure(bg=t["accent"], fg=t["text"])
        
        self.proc_card.configure(bg=t["accent"], highlightbackground=t["border"])
        self.proc_title.configure(bg=t["accent"], fg=t["text"])
        self.proc_text.configure(bg=t["accent"], fg=t["text"])