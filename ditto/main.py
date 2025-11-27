import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

from database import (
    init_db,
    get_recepty,
    get_recept,
    add_recept,
    update_recept,
    delete_recept,
    search_recepty
)


class DittoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ditto")
        self.geometry("420x500")
        self.configure(bg="#f3f3f3")

        container = tk.Frame(self, bg="#f3f3f3")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, SearchPage, DatabasePage, RecipePage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

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
        super().__init__(parent, bg="#f3f3f3")

        tk.Label(self,
            text="Ditto",
            font=("Arial", 22, "bold"),
            bg="#f3f3f3",
            fg="#222222"
        ).pack(pady=10)

        # ditto image in mainmenu
        if os.path.exists("ditto.jpg"):
            image = Image.open("ditto.jpg").resize((200, 200))
            self.img = ImageTk.PhotoImage(image)
            tk.Label(self, image=self.img, bg="#f3f3f3").pack(pady=10)
        else:
            tk.Label(self, text="[Chybí obrázek Ditto]",
                     bg="#f3f3f3", fg="#222222").pack(pady=30)

        ttk.Button(self, text="Vyhledavani", command=lambda: controller.show_frame("SearchPage")).pack(pady=10)
        ttk.Button(self, text="Databaze receptu", command=lambda: controller.show_frame("DatabasePage")).pack(pady=10)
        ttk.Button(self, text="Ukoncit", command=controller.quit).pack(pady=20)

# search page
class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f3f3")
        self.controller = controller
        self.ids = []

        tk.Label(
            self, 
            text="Vyhledavani receptu",
            font=("Arial", 16, "bold"),
            bg="#f3f3f3",
            fg="#222222"
        ).pack(pady=10)

        top = tk.Frame(self, bg="#f3f3f3")
        top.pack(pady=5)

        tk.Label(top, text="Hledat:", bg="#f3f3f3", fg="#222222").pack(side="left", padx=5)

        self.entry = ttk.Entry(top, width=22)
        self.entry.pack(sid="left", padx=5)
        self.entry.bind("<Return>", lambda e: self.do_search())

        self.combo = ttk.Combobox(top, state="readonly", width=10)
        self.combo["values"] = ("nazev", "cas", "suroviny")
        self.combo.current(0)
        self.combo.pack(side="left", padx=5)

        ttk.Button(top, text="Hledat", command=self.do_search).pack(side="left", padx=5)

        self.listbox = tk.Listbox(self, width=45, height=15)
        self.listbox.pack(pady=10)
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_recept())

        btn_frame = tk.Frame(self, bg="#f3f3f3")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Zobrazit", command=self.open_recept).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Zpet", command=lambda: controller.show_frame("MainMenu")).pack(side="left", padx=5)

    def refresh_all(self):
        self.listbox.delete(0, tk.END)
        self.ids = []
        for i, (rid, nazev, cas) in enumerate(get_recepty(), start=1):
            self.listbox.insert(tk.END, f"{i}, {nazev} ({cas})")
            self.ids.append(rid)

    def do_search(self):
        text = self.entry.get().strip()
        if not text:
            self.refresh_all()
            return

        mode_label = self.combo.get()
        if mode_label == "cas":
            mode = "cas"
        elif mode_label == "suroviny":
            mode = "suroviny"
        else:
            mode = "nazev"

        rows = search_recepty(text, mode)
        self.listbox.delete(0, tk.END)
        self.ids = []
        for i, (rid, nazev, cas) in enumerate(rows, start=1):
            self.listbox.insert(tk.END, f"{i}, {nazev} ({cas})")
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

    def open_recept(self):
        rid = self._get_selected_id()
        if rid is None:
            return
        recipe_page: "RecipePage" = self.controller.frames["RecipePage"]
        recipe_page.set_recept(rid)
        self.controller.show_frame("RecipePage")                                                                                            

# add recept window
class AddRecipeWindow(tk.Toplevel):
    def __init__(self, parent, on_saved, data=None):
        super().__init__(parent)
        self.title("Pridat recept" if data is None else "Upravit recept")
        self.geometry("400x500")
        self.on_saved = on_saved
        self.recept_id = None

        if data is None:
            data = ("", "", "", "")

        nazev0, cas0, suroviny0, postup0 = data

        tk.Label(self, text="Nazev:").pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_nazev = tk.Entry(self, width=40)
        self.entry_nazev.insert(0, nazev0)
        self.entry_nazev.pack(padx=10)

        tk.Label(self, text="Cas:").pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_cas = tk.Entry(self, width=40)
        self.entry_cas.insert(0, cas0)
        self.entry_cas.pack(padx=10)

        tk.Label(self, text="Suroviny:").pack(anchor="w", padx=10, pady=(10, 0))
        self.text_suroviny = tk.Text(self, width=40, height=5)
        self.text_suroviny.insert("1.0", suroviny0)
        self.text_suroviny.pack(padx=10)

        tk.Label(self, text="Postup:").pack(anchor="w", padx=10, pady=(10, 0))
        self.text_postup = tk.Text(self, width=40, height=8)
        self.text_postup.insert("1.0", postup0)
        self.text_postup.pack(padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Ulozit", command=self.save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zrusit", command=self.destroy).pack(side="left", padx=5)
    
    def set_id(self, rid):
        self.recept_id = rid

    def save(self):
        nazev = self.entry_nazev.get().strip()
        cas = self.entry_cas.get().strip()
        suroviny = self.text_suroviny.get("1.0", "end").strip()
        postup = self.text_postup.get("1.0", "end").strip()   

        if not nazev:
            messagebox.showwarning("Chyba", "Nazev je povinny.")
            return

        if self.recept_id is None:
            add_recept(nazev, cas, suroviny, postup)
        else:
            update_recept(self.recept_id, nazev, cas, suroviny, postup)        

        if self.on_saved:
            self.on_saved()
        self.destroy()    


# database page
class DatabasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f3f3")
        self.controller = controller
        self.ids = []

        top_frame = tk.Frame(self, bg="#f3f3f3")
        top_frame.pack(fill="x", pady=10)

        tk.Label(
            top_frame,
            text="Databaze receptu",
            font=("Arial", 16, "bold"),
            bg="#f3f3f3",
            fg="#222222"
        ).pack(side="left", padx=10)

        ttk.Button(top_frame, text="Pridat recept", command=self.open_add_window).pack(side="right", padx=10)

        self.listbox = tk.Listbox(self, width=45, height=15)
        self.listbox.pack(pady=10)

        btn_frame = tk.Frame(self, bg="#f3f3f3")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Zobrazit", command=self.open_recept).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Upravit", command=self.edit_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Smazat", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zpet", command=lambda: controller.show_frame("MainMenu")).pack(side="left", padx=5)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.ids = []
        for i, (rid, nazev, cas) in enumerate(get_recepty(), start=1):
            self.listbox.insert(tk.END, f"{i}. {nazev} ({cas})")
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
        recipe_page: "RecipePage" = self.controller.frames["RecipePage"]            
        recipe_page.set_recept(rid)
        self.controller.show_frame("RecipePage")

    def edit_selected(self):    
        rid = self._get_selected_id()
        if rid is None:
            return
        data = get_recept(rid)
        if data is None:
            return
        _, nazev, cas, suroviny, postup = data
        win = AddRecipeWindow(self, on_saved=self.refresh, data=(nazev, cas, suroviny, postup))
        win.set_id(rid)

    def delete_selected(self):
        rid = self._get_selected_id()
        if rid is None:
            return
        if messagebox.askyesno("Smazat", "Opravdu chces smazat tenhle recept?"):
            delete_recept(rid)
            self.refresh()    

# recipe details page 
class RecipePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f3f3")
        self.controller = controller

        self.title_label = tk.Label(self, text="",
                                    font=("Arial", 16, "bold"),
                                    bg="#f3f3f3",
                                    fg="#222222")
        self.title_label.pack(pady=10)
        self.info_label = tk.Label(self, text="", bg="#f3f3f3", fg="#222222")
        self.info_label.pack(pady=5)
        self.ing_label = tk.Label(self, text="", bg="#f3f3f3", wraplength=380, justify="left", fg="#222222")
        self.ing_label.pack(pady=5)
        self.proc_label = tk.Label(self, text="", bg="#f3f3f3", wraplength=380, justify="left", fg="#222222")
        self.proc_label.pack(pady=5)

        ttk.Button(self, text="Zpet na databazi",command=lambda: controller.show_frame("DatabasePage")).pack(pady=20)

    def set_recept(self, rid):
        data = get_recept(rid)
        if data is None:
            self.title_label.config(text="Recept nenalezen")
            self.info_label.config(text="")
            self.ing_label.config(text="")
            self.proc_label.config(text="")
            return

        _, nazev, cas, suroviny, postup = data
        self.title_label.config(text=nazev)
        self.info_label.config(text=f"Cas: {cas}")
        self.ing_label.config(text=f"Suroviny:\n{suroviny}")
        self.proc_label.config(text=f"Postup:\n{postup}")


if __name__ == "__main__":
    init_db()
    app = DittoApp()
    app.mainloop()
