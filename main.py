import sys
import time

from PyQt5 import QtGui
from PyQt5 import QtSql, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QItemSelection
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QTabWidget
from PyQt5.QtWidgets import QSplitter, QHeaderView
from PyQt5.QtWidgets import QWidget, QPushButton, QAction, QGridLayout, QTableView

from connectionDialog import ConnectionDialog
from database import Database
from exporter import Exporter

APP_NAME = "BugenPyQ SQL Client"


class MainUI(QMainWindow):
    connectedSignal = pyqtSignal([Database])
    disconnectedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        self.dbName = None
        self.db = None
        self.model = None

        self.tabs = QTabWidget(self)
        self.tab1 = DatabaseView(self)
        self.connectedSignal.connect(self.tab1.updateDbView)
        self.disconnectedSignal.connect(self.tab1.clear)
        self.tab2 = QueryView(self)
        self.tabs.addTab(self.tab1, "Database")
        self.tabs.addTab(self.tab2, "Query")
        self.setCentralWidget(self.tabs)
        self.setContentsMargins(0, 10, 0, 0)

        self.openSqliteAction = QAction("&Open SQLite...", self)
        self.openSqliteAction.setShortcut(QKeySequence.Open)
        self.openSqliteAction.triggered.connect(self.openSqlite)

        self.openPSqlAction = QAction("&Open PostgreSQL...", self)
        self.openPSqlAction.triggered.connect(lambda: self.openRemote('QPSQL'))

        self.openMySqlAction = QAction("&Open MySQL...", self)
        self.openMySqlAction.triggered.connect(lambda: self.openRemote('QMYSQL'))

        self.newSqliteAction = QAction("&New SQLite", self)
        self.newSqliteAction.setShortcut(QKeySequence.New)
        self.newSqliteAction.triggered.connect(self.createDb)

        self.submitAction = QAction("&Submit", self)
        self.submitAction.setShortcut(QKeySequence.Save)
        self.submitAction.triggered.connect(self.tab1.tableView.modelSubmit)

        self.refreshAction = QAction("&Refresh", self)
        self.refreshAction.setShortcut(QKeySequence.Refresh)
        self.refreshAction.triggered.connect(self.refresh)

        self.disconnectAction = QAction("&Close connection", self)
        self.disconnectAction.setShortcut(QKeySequence.Close)
        self.disconnectAction.triggered.connect(lambda: self.prepared(None))

        self.aboutQtAction = QAction("About Qt", self)
        self.aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self))

        self.aboutAction = QAction("About %s" % APP_NAME, self)
        self.aboutAction.triggered.connect(lambda:
                                           QtWidgets.QMessageBox.about(
                                               self, 'Bugen Zhao',
                                               'A simple SQL client written in PyQt by Bugen Zhao.'))

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&File")
        openMenu = fileMenu.addMenu("&Open")
        newMenu = fileMenu.addMenu("&New")

        openMenu.addAction(self.openSqliteAction)
        openMenu.addAction(self.openPSqlAction)
        openMenu.addAction(self.openMySqlAction)

        newMenu.addAction(self.newSqliteAction)

        fileMenu.addSeparator()
        fileMenu.addAction(self.submitAction)
        fileMenu.addAction(self.refreshAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.disconnectAction)

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.aboutQtAction)
        helpMenu.addAction(self.aboutAction)

        self.connectedSignal.connect(lambda: self.setWindowTitle(APP_NAME + ' - ' + self.dbName))
        self.disconnectedSignal.connect(lambda: self.setWindowTitle('%s' % APP_NAME))
        self.connectedSignal.connect(lambda: self.submitAction.setEnabled(True))
        self.disconnectedSignal.connect(lambda: self.submitAction.setEnabled(False))
        self.connectedSignal.connect(lambda: self.refreshAction.setEnabled(True))
        self.disconnectedSignal.connect(lambda: self.refreshAction.setEnabled(False))
        self.connectedSignal.connect(lambda: self.disconnectAction.setEnabled(True))
        self.disconnectedSignal.connect(lambda: self.disconnectAction.setEnabled(False))

        self.prepared(None)
        self.show()

    def prepared(self, dbName):
        if dbName is None or dbName == '':
            if self.db is not None:
                self.db.connection().close()
            self.dbName = None
            self.db = None
            self.disconnectedSignal.emit()
            self.statusBar().showMessage('Open a connection or new a database via "File" menu.')
        else:
            self.dbName = dbName
            self.connectedSignal.emit(self.db)
            self.statusBar().showMessage("Done: %s" % self.db.name, 8000)

    def refresh(self):
        self.connectedSignal.emit(self.db)

    def createDb(self):
        try:
            # 调用输入框获取数据库名称
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Create an SQLite database', '.', '*.sqlite')
            if filename.strip() != '':
                print(filename)
                self.db = Database("QSQLITE", name=filename)
                self.db.connection()

                if self.db.connection().isOpen():
                    self.prepared(filename)
                    self.db.connection().exec_("create table students(ID int primary key, "
                                               "name varchar(50), class varchar(50))")

                    self.db.connection().exec_("insert into students values(1, 'Bugen', 'F1803302')")
                    self.db.connection().exec_("insert into students values(2, 'Jack', 'F0101001')")
                    self.db.connection().exec_("insert into students values(3, 'Midori', 'F0101002')")
                    self.prepared(filename)
                    print('Done')
                else:
                    raise Exception
        except Exception as e:
            print(e)

    def openSqlite(self):
        if self.db is not None:
            self.disconnectedSignal.emit()

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open SQLite file', '.', '*.sqlite')
        if filename.strip() == '':
            return
        db = Database("QSQLITE", name=filename)
        db.connection()

        if db.connection().isOpen():
            self.db = db
            self.prepared(self.db.name)

    def openRemote(self, type='QPSQL'):
        if self.db is not None:
            self.disconnectedSignal.emit()

        dialog = ConnectionDialog(type)
        dialog.exec_()
        db = dialog.getDatabase()
        if db is None:
            return

        self.statusBar().showMessage('Connecting...')
        db.connection()

        if db.connection().isOpen():
            self.db = db
            self.prepared(self.db.name)
        else:
            self.statusBar().showMessage('Connection to %s failed : %s' % (db.name, db.connection().lastError().text())
                                         , 8000)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.db is None:
            event.accept()
        else:
            message = 'Are you sure you want to exit %s?' % APP_NAME
            message += '\n\nAll uncommitted changes to %s will be lost!' % self.db.name
            reply = QMessageBox.question(self, 'Confirm Exit', message)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()


class DatabaseView(QSplitter):
    def __init__(self, parent: MainUI):
        super().__init__()

        self.db = None

        self.tableListView = TableListView(parent)
        self.tableView = TableView(parent)
        self.tableView.statusBarMessageSignal.connect(parent.statusBar().showMessage)

        self.addWidget(self.tableListView)
        self.addWidget(self.tableView)

        self.setOrientation(Qt.Horizontal)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 3)

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
                "WHERE type = 'table' "
                "ORDER BY name;",
                db=db.connection())
        elif db.type == 'QMYSQL':
            self.model.setQuery(
                "SELECT TABLE_NAME FROM information_schema.tables "
                "WHERE TABLE_SCHEMA = 'test' "
                "ORDER BY TABLE_NAME;",
                db=db.connection())
        elif db.type == 'QPSQL':
            self.model.setQuery(
                "SELECT tablename FROM pg_tables "
                "WHERE tablename NOT LIKE 'pg%' AND tablename NOT LIKE 'sql_%' "
                "ORDER BY tablename;",
                db=db.connection())
        self.model.query()
        self.model.setHeaderData(0, Qt.Horizontal, "Table")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class TableView(QTableView):
    statusBarMessageSignal = pyqtSignal([str, int])

    def __init__(self, parent: QWidget):
        super().__init__()
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
        # if db.type == 'QPSQL':
        #     self.model = QtSql.QSqlQueryModel()
        #     self.setModel(self.model)
        #     self.model.setQuery('SELECT * FROM %s' % tableName, db=db.connection())
        #     self.model.query()
        #     print('postgres: ', self.model.lastError().text())
        #     return

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

    def modelSubmit(self):
        try:
            ret = self.model.submitAll()
            if not ret:
                raise Exception
            self.statusBarMessageSignal.emit("Submit success", 1000)
            print("Submit success")
        except:
            self.statusBarMessageSignal.emit("Submit failed", 1000)
            print("Submit failed")
        # self.mainUI.refresh()

    def exportCsv(self):
        if self.model is None:
            return
        Exporter().exportCsv(self, self.model)


class QueryView(QWidget):
    def __init__(self, mainUI: MainUI):
        super().__init__()
        self.queryInput = QtWidgets.QPlainTextEdit()
        self.queryButton = QPushButton("Query")
        self.queryButton.clicked.connect(lambda: self.doQuery(self.queryInput.toPlainText()))
        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.exportCsv)
        self.resultTable = QTableView()

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
        self.mainUI = mainUI

        mainUI.connectedSignal.connect(self.updateQueryView)
        mainUI.disconnectedSignal.connect(self.clear)
        mainUI.connectedSignal.connect(lambda: self.queryInput.setEnabled(True))
        mainUI.disconnectedSignal.connect(lambda: self.queryInput.setEnabled(False))
        mainUI.connectedSignal.connect(lambda: self.queryButton.setEnabled(True))
        mainUI.disconnectedSignal.connect(lambda: self.queryButton.setEnabled(False))
        mainUI.connectedSignal.connect(lambda: self.exportButton.setEnabled(True))
        mainUI.disconnectedSignal.connect(lambda: self.exportButton.setEnabled(False))

    def clear(self):
        self.db = None
        self.queryInput.clear()
        if self.resultTable.model() is not None:
            self.resultTable.model().removeRows(0, self.resultTable.model().rowCount())
        self.model = None

    def doQuery(self, query: str):
        if self.db is None:
            return
        self.model = QtSql.QSqlQueryModel()

        self.resultTable.setModel(self.model)
        self.model.setQuery(query, db=self.db.connection())
        t0 = time.time()
        self.model.query()
        t1 = time.time()
        dt = t1 - t0
        message = 'Done in %.3f s with the result: ' % dt
        if self.model.lastError().type() == self.model.lastError().NoError:
            message += 'OK'
        else:
            message += self.model.lastError().text()
        self.mainUI.statusBar().showMessage(message, 8000)
        # print(self.model.lastError().type())

    def updateQueryView(self, db: Database):
        self.db = db
        self.queryInput.setPlainText('SELECT * FROM ')
        if self.resultTable.model() is not None:
            self.resultTable.model().removeRows(0, self.resultTable.model().rowCount())

    def exportCsv(self):
        if self.model is None:
            return
        Exporter().exportCsv(self, self.model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    sys.exit(app.exec_())
