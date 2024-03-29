import time

from PyQt5 import QtSql, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QAction, QGridLayout, QTableView

from database import Database
from exporter import Exporter


class QueryView(QWidget):
    statusBarMessageSignal = pyqtSignal([str, int])

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.queryInput = QtWidgets.QPlainTextEdit()
        self.queryButton = QPushButton("Query")
        self.queryButton.clicked.connect(lambda: self.doQuery(self.queryInput.toPlainText()))
        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.exportCsv)
        self.resultTable = QTableView()

        self.queryInput.setPlainText('SELECT * FROM ')

        exportAction = QAction("Export to CSV")
        exportAction.triggered.connect(self.exportCsv)
        self.resultTable.addAction(exportAction)

        self.resultTable.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.queryInput, 0, 0, 2, 1)
        self.layout.addWidget(self.queryButton, 0, 1)
        self.layout.addWidget(self.exportButton, 1, 1)
        self.layout.addWidget(self.resultTable, 2, 0, 1, 2)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(2, 5)

        self.model = None
        self.db = None

    def clear(self):
        self.db = None
        if self.resultTable.model() is not None:
            self.resultTable.model().removeRows(0, self.resultTable.model().rowCount())
        self.model = None

    def doQuery(self, query: str):
        if self.db is None:
            return
        self.model = QtSql.QSqlQueryModel()

        self.resultTable.setModel(self.model)

        class QueryThread(QThread):
            def __init__(self, parent: QueryView):
                super().__init__(parent)
                self.queryView = parent

            def run(self) -> None:
                t0 = time.time()
                self.queryView.model.setQuery(query, db=self.queryView.db.connection())
                self.queryView.model.query()
                t1 = time.time()
                dt = t1 - t0
                message = 'Done in %.3f s with the result: ' % dt
                if self.queryView.model.lastError().type() == self.queryView.model.lastError().NoError:
                    message += 'OK'
                else:
                    message += self.queryView.model.lastError().text()

                self.queryView.statusBarMessageSignal.emit(message, 8000)

        def onQueryFinished():
            self.resultTable.resizeColumnsToContents()
            self.exportButton.setEnabled(True)
            self.queryButton.setEnabled(True)

        def onQueryStarted():
            self.exportButton.setEnabled(False)
            self.queryButton.setEnabled(False)

        thread = QueryThread(self)
        thread.started.connect(onQueryStarted)
        thread.finished.connect(onQueryFinished)

        thread.start()

    def updateQueryView(self, db: Database):
        self.db = db
        if self.resultTable.model() is not None:
            self.resultTable.model().removeRows(0, self.resultTable.model().rowCount())

    def exportCsv(self):
        if self.model is None:
            return
        Exporter().exportCsv(self, self.model)

    def setBzEnabled(self, enabled: bool):
        self.queryInput.setEnabled(enabled)
        self.queryButton.setEnabled(enabled)
        self.exportButton.setEnabled(enabled)
