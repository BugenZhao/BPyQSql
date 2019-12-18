from PyQt5 import QtSql, QtWidgets
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtCore import pyqtSignal, QItemSelection
from PyQt5.QtWidgets import QSplitter, QHeaderView
from PyQt5.QtWidgets import QWidget, QAction, QTableView

from database import Database
from exporter import Exporter


class DatabaseView(QSplitter):
    statusBarMessageSignal = pyqtSignal([str, int])

    def __init__(self, parent: QWidget):
        super().__init__()

        self.db = None

        self.tableListView = TableListView(parent)
        self.tableView = TableView(parent)

        self.addWidget(self.tableListView)
        self.addWidget(self.tableView)

        self.setOrientation(Qt.Horizontal)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 5)

    def clear(self):
        self.db = None
        self.tableView.clear()
        self.tableListView.clear()

    def updateDbView(self, db: Database):
        self.db = db
        self.tableListView.updateDb(db)
        if self.tableView.model is not None:
            self.tableView.model.clear()
        # selectionModel will appear only after model has been set
        self.tableListView.selectionModel().selectionChanged.connect(
            lambda selected, _: self.tableView.updateTable(self.db, selected))
        self.tableListView.selectionModel().select(self.tableListView.model.index(0, 0), QItemSelectionModel.Select)
        self.tableListView.setFocus()

    def modelSubmit(self):
        ret = self.tableView.modelSubmit()
        if ret:
            self.statusBarMessageSignal.emit('Submit success', 3000)
        else:
            self.statusBarMessageSignal.emit('Submit failed', 3000)


class TableListView(QtWidgets.QTableView):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.model = None
        self.setSelectionMode(self.SingleSelection)

    def clear(self):
        if self.model is not None:
            self.model.clear()
            self.model = None

    def updateDb(self, db: Database):
        self.model = QtSql.QSqlQueryModel()
        self.setModel(self.model)
        if db.type == 'QSQLITE':
            self.model.setQuery(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table'  AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name;",
                db=db.connection())
        elif db.type == 'QMYSQL':
            self.model.setQuery(
                "SELECT TABLE_NAME FROM information_schema.tables "
                "WHERE TABLE_SCHEMA = '%s' "
                "ORDER BY TABLE_NAME;" % db.connection().databaseName(),
                db=db.connection())
        elif db.type == 'QPSQL':
            self.model.setQuery(
                "SELECT tablename FROM pg_tables "
                "WHERE tablename NOT LIKE 'pg%' AND tablename NOT LIKE 'sql_%'"
                "ORDER BY tablename;",
                db=db.connection())
        self.model.query()
        self.model.setHeaderData(0, Qt.Horizontal, "Table")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class TableView(QTableView):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.model = None

        exportAction = QAction("Export to CSV")
        exportAction.triggered.connect(self.exportCsv)
        self.addAction(exportAction)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def clear(self):
        if self.model is not None:
            self.model.clear()
            self.model = None

    def doUpdateTable(self, db: Database, tableName: str):
        self.model = QtSql.QSqlTableModel(db=db.connection())
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.setModel(self.model)
        self.model.setTable(tableName)
        self.model.select()
        self.resizeColumnsToContents()

    def updateTable(self, db: Database, selected: QItemSelection):
        index = selected.indexes()[0]
        tableName = selected.indexes()[0].model().data(index)
        print(tableName)
        self.doUpdateTable(db, tableName)

    def modelSubmit(self) -> bool:
        try:
            return self.model.submitAll()
        except:
            return False

    def exportCsv(self):
        if self.model is None:
            return
        Exporter().exportCsv(self, self.model)
