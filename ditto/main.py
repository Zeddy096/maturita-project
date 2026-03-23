import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from database import (
    init_db,
    get_recepty,
    get_recept,
    add_recept,
    update_recept,
    delete_recept,
    search_recepty,
    save_image_for_recipe,
)

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


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
        "TButton",
        font=("Arial", 11, "bold"),
        padding=10,
    )    

    style.configure(
        "TEntry",
        padding=6
    )

    style.configure(
        "TCombobox",
        padding=5
    )

    style.configure(
        "TRadiobutton",
        background="#ffffff",
        font=("Arial", 10)
    )

def bind_scroll_recursive(widget, canvas):
    def _on_mousewheel(event):

        # linux (button 4 & 5)
        if hasattr(event, "num"):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            return

        # windows / touchpad
        if hasattr(event, "delta") and event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 240)), "units")

    widget.bind("<MouseWheel>", _on_mousewheel)
    widget.bind("<Button-4>", _on_mousewheel)
    widget.bind("<Button-5>", _on_mousewheel)

    for child in widget.winfo_children():
        bind_scroll_recursive(child, canvas)


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

        self.dark_mode = False
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

    def _setup_style(self):
        self.configure(bg=self.theme["root_bg"])

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Custom.TButton",
            font=("Arial", 11, "bold"),
            padding=10,
            background=self.theme["button"],
            foreground=self.theme["text"],
            borderwidth=0,
            relief="flat",
            focusthickness=0,
            focuscolor=self.theme["button"],
            lightcolor=self.theme["button"],
            darkcolor=self.theme["button"],
            highlightthickness=0
        )

        style.map(
            "Custom.TButton",
            background=[
                ("active", self.theme["button_active"]),
                ("pressed", self.theme["button_active"]),
                ("!disabled", self.theme["button"])
            ],
            foreground=[
                ("active", self.theme["text"]),
                ("pressed", self.theme["text"]),
                ("!disabled", self.theme["text"])
            ],
            lightcolor=[("!disabled", self.theme["button"])],
            darkcolor=[("!disabled", self.theme["button"])],
            bordercolor=[("!disabled", self.theme["button"])],
            focuscolor=[("!disabled", self.theme["button"])]
        )

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME

        self._setup_style()
        self.container.configure(bg=self.theme["root_bg"])

        for frame in self.frames.values():
            if hasattr(frame, "apply_theme"):
                frame.apply_theme()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "DatabasePage":
            frame.refresh()
        if page_name == "SearchPage":
            frame.refresh_all()            
        frame.tkraise()


# main menu
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
            text="Dark mode",
            style="Custom.TButton",
            command=self.controller.toggle_theme
        )
        self.toggle_btn.pack(side="right")

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

        if self.controller.dark_mode:
            self.toggle_btn.configure(text="Light mode")
        else:
            self.toggle_btn.configure(text="Dark mode")


# search page
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
            selectbackground="#bfa8ea" if not self.controller.dark_mode else "#5a4a7c",
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
            selectbackground="#bfa8ea" if not self.controller.dark_mode else "#5a4a7c",
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


# add recept window
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


# database page
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
            selectbackground="#bfa8ea" if not self.controller.dark_mode else "#5a4a7c",
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
            selectbackground="#bfa8ea" if not self.controller.dark_mode else "#5a4a7c",
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


# recipe details page 
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
            self._set_text(self.ing_text, "")
            self._set_text(self.proc_text, "")
            self.img_label.config(image="", text="")
            self._img_ref = None
            return

        rid_db, nazev, cas, suroviny, postup, *rest = data
        cas_min = rest[0] if len(rest) > 0 else None
        image_path = rest[1] if len(rest) > 1 else None

        self.title_label.config(text=nazev)
        self._fit_title(nazev)

        if cas_min is None or cas_min == "":
            self.info_label.config(text="Čas: -")
        else:
            self.info_label.config(text=f"Čas: {cas_min} min")

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

        self.ing_card.configure(bg=t["accent"], highlightbackground=t["border"])
        self.ing_title.configure(bg=t["accent"], fg=t["text"])
        self.ing_text.configure(bg=t["accent"], fg=t["text"])
        
        self.proc_card.configure(bg=t["accent"], highlightbackground=t["border"])
        self.proc_title.configure(bg=t["accent"], fg=t["text"])
        self.proc_text.configure(bg=t["accent"], fg=t["text"])

if __name__ == "__main__":
    init_db()
    app = DittoApp()
    app.mainloop()
