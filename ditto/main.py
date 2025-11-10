# main.py -- spouští aplikaci
import sys
from PySide6.QtWidgets import QApplication
from ui_main import MainWindow
from database import Database

def main():
    db = Database("data/recepty.db")
    app = QApplication(sys.argv)
    window = MainWindow(db)
    window.resize(900, 1100)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
