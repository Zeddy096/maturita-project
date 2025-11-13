import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTK
import os

class DittoApp(tk.Tk)>
    def __innit__(self)>
        super().__innit__()
        self.title("Ditto")
        self.geometry("420x550")
        self.configure(bg="#f3f3f3")

        # main container
        container = tk.Frame(self)
        container.ppack(fill="both", expand=True)

        # all frames
        self.frames = ()
        for F in (MainMenu, SearchPage, DatabasePage, RecipePage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


# main menu
class MainMenu(tk.Frame):
    def __innit__(self, parent, controller):
        super().__innit__(parent, bg="#f3f3f3")

        tk.Label(self, text="Ditto", font=("Arial", 22, "bold"), bg="#f3f3f3").pack(pady=10)

        # ditto image in mainmenu
        if os.path.exists("ditto.jpg"):
            image = Image.open("ditto.jpg")resize((200, 200))
            self.img = ImageTk.PhotoImage(image)
            tk.Label(self, image=self.img, bg="#f3f3f3").pack(pady=10)
        else:
            tk.Label(self, text="(Ditto.jpg missing)", bg="#f3f3f3").pack(pady=30)

        ttk.Button(self, text="Vyhledavani", command=lambda:
controller.show_frame("SearchPage")).pack(pady=10)
        ttk.Button(self, text="Databaze receptu", command=lambda:
controller.show_frame("DatabasePage")).pack(pady=10)
        ttk.Button(self, text="Ukoncit", command=controller.quit).pack(pady=20)

# search page
class SearchPage(tk.Frame):
    def __innit__(self, parent, controller):
        super().__innit__(parent, bg="#f3f3f3")

        tk.Label(self, text="Vyhledavani receptu", font=("Afrial", 16, "bold"), bg="#f3f3f3").pack(pady=10)
        ttk.Entry(self, width=30).pack(pady=5)
        ttk.Button(self, text="Zpet", command=lambda: controller.show_frame("MainMenu")).pack(pady=20)


# database page
class DatabasePage(tk.Frame):
    def __innit__(self, parent, controller):
        super().__innit__(parent, bg="#f3f3f3")

        tk.Label(self, text="databaze receptu", font=("Afrial", 16, "bold"), bg="#f3f3f3").pack(pady=10)

        # recepty
        ttk.Button(self, text="Recept1", command=lambda: controller.show_frame("RecipePage")).pack(pady=5)
        ttk.Button(self, text="Recept2", command=lambda: controller.show_frame("RecipePage")).pack(pady=5)

        ttk.Button(self, text="Zpet", command=lambda: controller.show_frame("MainMenu")).pack(pady=20)

# recipe details page 
class RecipePage(tk.Frame):
    def __innit__(self, parent, controller):
        super().__innit__(parent, bg="#f3f3f3")

        tk.Label(self, text="Recept1", font=("Arial", 16, "bold"), bg="#f3f3f3").pack(pady=10)
        tk.Label(self, text="cas: 20 minut", bg="#f3f3f3").pack()
        tk.Label(self, text="suroviny: mouka, vejce, mleko", bg="#f3f3f3").pack()
        tk.Label(self, text="postup: smichej a pec", bg="#f3f3f3").pack(pady=10)

        ttk.Button(self, text="Zpet na databazi", command=lambda:
controller.show_frame("DatabasePage")).pack(pady=20)

if __name__ == "__main__":
    app = DittoApp()
    app.mainloop()
