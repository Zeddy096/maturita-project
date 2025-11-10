# ui_search.py -- vyhledávání receptů
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QComboBox
)
from PySide6.QtCore import Qt

class SearchWidget(QWidget):
    def __init__(self, db, show_recept):
        super().__init__()
        self.db = db
        self.show_recept = show_recept

        layout = QVBoxLayout()
        top = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["recept", "cas", "suroviny"])
        top.addWidget(QLabel("Vyhledávání:"))
        top.addWidget(self.filter_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Zadej hledaný výraz...")
        self.search_input.returnPressed.connect(self.do_search)
        btn_search = QPushButton("Hledej")
        btn_search.clicked.connect(self.do_search)

        top.addWidget(self.search_input)
        top.addWidget(btn_search)
        layout.addLayout(top)

        self.results = QListWidget()
        self.results.itemActivated.connect(self.on_select)
        layout.addWidget(self.results)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        # zobrazit všechny recepty
        self.results.clear()
        for r in self.db.get_all_recepty():
            item = QListWidgetItem(f"{r['nazev']}  —  Čas: {r['cas'] or '-'}")
            item.setData(Qt.UserRole, r["id"])
            self.results.addItem(item)

    def do_search(self):
        q = self.search_input.text().strip()
        f = self.filter_combo.currentText()
        if not q:
            self.refresh()
            return
        rows = self.db.search_recepty(q, filter_by=("cas" if f == "cas" else ("suroviny" if f == "suroviny" else "nazev")))
        self.results.clear()
        for r in rows:
            item = QListWidgetItem(f"{r['nazev']}  —  Čas: {r['cas'] or '-'}")
            item.setData(Qt.UserRole, r["id"])
            self.results.addItem(item)

    def on_select(self, item: QListWidgetItem):
        rid = item.data(Qt.UserRole)
        self.show_recept(rid)
