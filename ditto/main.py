from database import init_db
from components.ui_app import DittoApp

if __name__ == "__main__":
    init_db()
    app = DittoApp()
    app.mainloop()
