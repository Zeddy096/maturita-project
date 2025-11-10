# ui_database.py -- seznam receptů, přidání, úpravy, smazání
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QMessageBox, QDialog, QFormLayout, QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt

class AddEditDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Přidat recept" if data is None else "Upravit recept")
        self.data = data or {}
        form = QFormLayout()
        self.name = QLineEdit(self.data.get("nazev", ""))
        self.cas = QLineEdit(self.data.get("cas", ""))
        self.suroviny = QTextEdit(self.data.get("suroviny", ""))
        self.postup = QTextEdit(self.data.get("postup", ""))
        form.addRow("Název:", self.name)
        form.addRow("Čas:", self.cas)
        form.addRow("Suroviny:", self.suroviny)
        form.addRow("Postup:", self.postup)

        btn_ok = QPushButton("Uložit")
        btn_cancel = QPushButton("Storno")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        h = QHBoxLayout()
        h.addWidget(btn_ok)
        h.addWidget(btn_cancel)
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(h)
        self.setLayout(layout)

    def values(self):
        return {
            "nazev": self.name.text().strip(),
            "cas": self.cas.text().strip(),
            "suroviny": self.suroviny.toPlainText().strip(),
            "postup": self.postup.toPlainText().strip()
        }

class DatabaseWidget(QWidget):
    def __init__(self, db, show_recept):
        super().__init__()
        self.db = db
        self.show_recept = show_recept
        layout = QVBoxLayout()

        top = QHBoxLayout()
        lbl = QLabel("Databáze receptů")
        btn_add = QPushButton("Přidat")
        btn_add.clicked.connect(self.add_recept)
        top.addWidget(lbl)
        top.addStretch()
        top.addWidget(btn_add)
        layout.addLayout(top)

        self.listw = QListWidget()
        self.listw.itemActivated.connect(self.open_recept)
        layout.addWidget(self.listw)

        # vytvořit edit/smaz tlačítka pod seznamem
        btns = QHBoxLayout()
        btn_edit = QPushButton("Upravit vybraný")
        btn_del = QPushButton("Smazat vybraný")
        btn_edit.clicked.connect(self.edit_selected)
        btn_del.clicked.connect(self.delete_selected)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_del)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.listw.clear()
        for r in self.db.get_all_recepty():
            item = QListWidgetItem(f"{r['nazev']}    (Čas: {r['cas'] or '-'})")
            item.setData(Qt.UserRole, r["id"])
            self.listw.addItem(item)

    def add_recept(self):
        dlg = AddEditDialog(self)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            if not vals["nazev"]:
                QMessageBox.warning(self, "Chyba", "Název je povinný.")
                return
            self.db.add_recept(vals["nazev"], vals["cas"], vals["suroviny"], vals["postup"])
            self.refresh_list()

    def get_selected_id(self):
        it = self.listw.currentItem()
        if not it:
            return None
        return it.data(Qt.UserRole)

    def edit_selected(self):
        rid = self.get_selected_id()
        if not rid:
            QMessageBox.information(self, "Info", "Vyber recept.")
            return
        r = self.db.get_recept(rid)
        dlg = AddEditDialog(self, r)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            self.db.update_recept(rid, vals["nazev"], vals["cas"], vals["suroviny"], vals["postup"])
            self.refresh_list()

    def delete_selected(self):
        rid = self.get_selected_id()
        if not rid:
            QMessageBox.information(self, "Info", "Vyber recept.")
            return
        okay = QMessageBox.question(self, "Smazat", "Opravdu smazat recept?")
        if okay == QMessageBox.StandardButton.Yes:
            self.db.delete_recept(rid)
            self.refresh_list()

    def open_recept(self, item):
        rid = item.data(Qt.UserRole)
        self.show_recept(rid)
