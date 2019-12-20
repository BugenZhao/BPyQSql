import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtSql import QSql
from PyQt5.QtWidgets import QAction, QStyle, QHBoxLayout, QWidget
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QTabWidget

from connectionDialog import ConnectionDialog
from database import Database
from databaseView import DatabaseView
from example import EXAMPLE_SQLITE
from queriesContainer import QueriesContainer

APP_NAME = "BugenPyQ SQL Client"


class MainUI(QMainWindow):
    connectedSignal = pyqtSignal([Database])
    disconnectedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.resize(1000, 600)

        self.dbName = None
        self.db = None

        self.databaseView = DatabaseView(self)
        self.connectedSignal.connect(self.databaseView.updateDbView)
        self.disconnectedSignal.connect(self.databaseView.clear)
        self.databaseView.statusBarMessageSignal.connect(self.statusBar().showMessage)

        self.queriesContainer = QueriesContainer(self)
        self.connectedSignal.connect(self.queriesContainer.updateQueryView)
        self.disconnectedSignal.connect(self.queriesContainer.clear)
        self.connectedSignal.connect(lambda: self.queriesContainer.setBzEnabled(True))
        self.disconnectedSignal.connect(lambda: self.queriesContainer.setBzEnabled(False))
        self.queriesContainer.statusBarMessageSignal.connect(self.statusBar().showMessage)

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.databaseView, "Database")
        self.tabs.addTab(self.queriesContainer, "Query")

        window = QWidget(self)
        layout = QHBoxLayout(window)
        layout.addWidget(self.tabs)
        layout.setContentsMargins(2, 8, 2, 2)
        window.setLayout(layout)
        self.setCentralWidget(window)

        toolBar = self.addToolBar("Main")
        toolBar.setIconSize(QSize(24, 24))
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.openSqliteAction = QAction("Open &SQLite...", self)
        self.openSqliteAction.setShortcut(QKeySequence.Open)
        self.openSqliteAction.triggered.connect(self.openSqlite)

        self.openPSqlAction = QAction("Open &PostgreSQL...", self)
        self.openPSqlAction.triggered.connect(lambda: self.openRemote('QPSQL'))

        self.openMySqlAction = QAction("Open &MySQL...", self)
        self.openMySqlAction.triggered.connect(lambda: self.openRemote('QMYSQL'))

        self.newSqliteAction = QAction("&New SQLite Example", self)
        self.newSqliteAction.setShortcut(QKeySequence.New)
        self.newSqliteAction.triggered.connect(self.createDb)

        self.addTabAction = QAction("Add Query Tab", self)
        self.addTabAction.setShortcut(QKeySequence.AddTab)
        self.addTabAction.triggered.connect(self.queriesContainer.addTab)

        self.submitAction = QAction("&Submit", self)
        self.submitAction.setShortcut(QKeySequence.Save)
        self.submitAction.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.submitAction.triggered.connect(self.databaseView.modelSubmit)

        self.refreshAction = QAction("&Refresh", self)
        self.refreshAction.setShortcut(QKeySequence.Refresh)
        self.refreshAction.setIcon(QApplication.style().standardIcon(QStyle.SP_BrowserReload))
        self.refreshAction.triggered.connect(self.refresh)

        self.disconnectAction = QAction("&Close Connection", self)
        self.disconnectAction.setShortcut(QKeySequence.Close)
        self.disconnectAction.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.disconnectAction.triggered.connect(self.closeConnection)

        self.aboutQtAction = QAction("About Qt", self)
        self.aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self))

        self.aboutAction = QAction("About %s" % APP_NAME, self)
        self.aboutAction.triggered.connect(lambda:
                                           QtWidgets.QMessageBox.about(
                                               self, 'Bugen Zhao',
                                               'A simple SQL client written in PyQt by BugenZhao (aka Ziqi Zhao).'
                                               '\nFor the final project of course CS902.'))

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&File")
        openMenu = fileMenu.addMenu("&Open")
        newMenu = fileMenu.addMenu("&New")

        openMenu.addAction(self.openSqliteAction)
        openMenu.addAction(self.openPSqlAction)
        openMenu.addAction(self.openMySqlAction)

        newMenu.addAction(self.newSqliteAction)

        fileMenu.addAction(self.addTabAction)

        fileMenu.addSeparator()
        fileMenu.addAction(self.submitAction)
        fileMenu.addAction(self.refreshAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.disconnectAction)

        toolBar.addAction(self.submitAction)
        toolBar.addAction(self.refreshAction)
        toolBar.addSeparator()
        toolBar.addAction(self.disconnectAction)

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
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Create an SQLite database', '.', '*.sqlite')
            if filename.strip() != '':
                print(filename)
                self.db = Database("QSQLITE", name=filename)
                self.db.connection()

                if self.db.connection().isOpen():
                    self.prepared(filename)
                    for line in EXAMPLE_SQLITE.split('\n'):
                        self.db.connection().exec(line)
                    self.prepared(filename)
                    print('Done')
                else:
                    raise Exception
        except Exception as e:
            print(e)

    def openSqlite(self):
        if not self.closeConnection():
            return

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open SQLite file', '.', '*.sqlite')
        if filename.strip() == '':
            return
        db = Database("QSQLITE", name=filename)
        db.connection()

        if db.connection().isOpen():
            self.db = db
            self.prepared(self.db.name)
            print(db.connection().tables(QSql.Tables))

    def openRemote(self, type='QPSQL'):
        if not self.closeConnection():
            return

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
            print(db.connection().tables(QSql.Tables))
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

    def closeConnection(self) -> bool:
        if self.db is None:
            return True
        else:
            message = 'Are you sure you want to close connection %s?' % self.db.name
            message += '\n\nAll uncommitted changes to %s will be lost!' % self.db.name
            reply = QMessageBox.question(self, 'Confirm Close', message)
            if reply == QMessageBox.Yes:
                self.prepared(None)
                return True
            else:
                return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    sys.exit(app.exec_())
