# ui_recept.py -- detail receptu
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QFrame
from PySide6.QtCore import Qt

class ReceptWidget(QWidget):
    def __init__(self, db, on_back):
        super().__init__()
        self.db = db
        self.on_back = on_back
        self.current_id = None

        layout = QVBoxLayout()
        top = QHBoxLayout()
        btn_back = QPushButton("Zpět")
        btn_back.clicked.connect(self.on_back)
        self.title = QLabel("Název receptu")
        self.title.setStyleSheet("font-size:20px; font-weight:bold;")
        top.addWidget(btn_back)
        top.addStretch()
        top.addWidget(self.title)
        layout.addLayout(top)

        self.box = QTextEdit()
        self.box.setReadOnly(True)
        self.box.setFrameStyle(QFrame.Box)
        layout.addWidget(self.box)

        self.setLayout(layout)

    def load_recept(self, rid):
        r = self.db.get_recept(rid)
        if not r:
            self.title.setText("Recept nenalezen")
            self.box.setPlainText("")
            return
        self.current_id = rid
        self.title.setText(r["nazev"])
        text = f"Čas: {r['cas']}\n\nsuroviny:\n{r['suroviny']}\n\npostup:\n{r['postup']}"
        self.box.setPlainText(text)
