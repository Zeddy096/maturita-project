# ui_main.py -- hlavní okno + navigace mezi obrazovkami
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt
from ui_search import SearchWidget
from ui_database import DatabaseWidget
from ui_recept import ReceptWidget

class HomeWidget(QWidget):
    def __init__(self, switch):
        super().__init__()
        self.switch = switch
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        title = QLabel("Ditto")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:28px; margin:10px;")
        layout.addWidget(title)

        # jednoduché "ilustrační" místo pro obrázek
        pic = QLabel()
        pic.setFixedSize(220, 220)
        pic.setFrameStyle(QFrame.Box)
        pic.setText("🧁 Ditto (image)")
        pic.setAlignment(Qt.AlignCenter)
        layout.addWidget(pic, alignment=Qt.AlignHCenter)

        # tlačítka
        btn_layout = QVBoxLayout()
        btn_search = QPushButton("Vyhledávání")
        btn_db = QPushButton("Databáze receptů")
        btn_quit = QPushButton("Ukončit")

        btn_search.clicked.connect(lambda: self.switch("search"))
        btn_db.clicked.connect(lambda: self.switch("database"))
        btn_quit.clicked.connect(lambda: self.switch("quit"))

        btn_layout.addWidget(btn_search)
        btn_layout.addWidget(btn_db)
        btn_layout.addWidget(btn_quit)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Ditto — recepty")
        self.stack = QStackedWidget()
        self.pages = {}

        # vytváříme stránky a předáme callback pro přepínání
        self.home = HomeWidget(self._switch)
        self.search = SearchWidget(self.db, show_recept=self.show_recept)
        self.database = DatabaseWidget(self.db, show_recept=self.show_recept)
        self.recept = ReceptWidget(self.db, on_back=lambda: self._switch("database"))

        self._add_page("home", self.home)
        self._add_page("search", self.search)
        self._add_page("database", self.database)
        self._add_page("recept", self.recept)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self._switch("home")

    def _add_page(self, name, widget):
        self.pages[name] = widget
        self.stack.addWidget(widget)

    def _switch(self, name):
        if name == "quit":
            self.close()
            return
        widget = self.pages.get(name)
        if widget is not None:
            self.stack.setCurrentWidget(widget)
            # refresh some pages when shown
            if name == "database":
                self.database.refresh_list()
            if name == "search":
                self.search.refresh()

    def show_recept(self, recept_id):
        # nastavíme recept do ReceptWidget a přepneme
        self.recept.load_recept(recept_id)
        self._switch("recept")
