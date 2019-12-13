import time

from AppKit import *
from PyQt5 import QtGui, QtSql, QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QItemSelection, QFile
from PyQt5.QtGui import QKeySequence
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QMainWindow, QAction, QInputDialog, \
    QTabWidget, QSplitter, QGridLayout, QTableView, QMacCocoaViewContainer


class DataBase:
    def __init__(self, type: str, name: str = '', useName: str = ''):
        self.db = None
        self.type = type
        self.name = name
        self.useName = useName
        self.connName = str(hash(type + name))

    def connection(self) -> QSqlDatabase:
        if self.db is not None:
            return self.db

        db = QtSql.QSqlDatabase.addDatabase(self.type, self.connName)
        if self.type == 'QSQLITE':
            db.setDatabaseName(self.name)
        elif self.type == 'QMYSQL':
            db.setHostName('115.159.1.64')
            db.setPort(3306)
            db.setUserName('root')
            db.setPassword('trpb(g5(HiWx')
            db.setDatabaseName(self.name)

        db.open()
        self.db = db
        return self.db


class MainUI(QMainWindow):
    connectedSignal = pyqtSignal([DataBase])
    disconnectedSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        frame = Foundation.NSMakeRect(0, 0, self.width(), self.height())
        view = objc.objc_object(c_void_p=self.winId().__int__())

        visualEffectView = NSVisualEffectView.new()
        visualEffectView.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        visualEffectView.setWantsLayer_(True)
        visualEffectView.setFrame_(frame)
        visualEffectView.setState_(NSVisualEffectStateActive)
        # visualEffectView.setMaterial_(NSVisualEffectMaterialUltraDark)
        visualEffectView.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        visualEffectView.setWantsLayer_(True)

        self.setAttribute(Qt.WA_TranslucentBackground, True)

        window = view.window()
        content = window.contentView()

        container = QMacCocoaViewContainer(0, self)
        content.addSubview_positioned_relativeTo_(visualEffectView, NSWindowBelow, container)

        window.setTitlebarAppearsTransparent_(True)
        window.setStyleMask_(window.styleMask() | NSFullSizeContentViewWindowMask)

        appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')

        self.statusBar()
        self.resize(800, 600)

        self.dbName = None
        self.db = None
        self.model = None

        self.tabs = QTabWidget(self)
        self.tab1 = DataBaseView(self)
        self.tab2 = QueryView(self)
        self.tabs.addTab(self.tab1, "Database")
        self.tabs.addTab(self.tab2, "Query")
        self.setCentralWidget(container)
        layout = QGridLayout()
        layout.addWidget(self.tabs, 0, 0)
        self.setContentsMargins(0, 20, 0, 0)
        container.setLayout(layout)

        self.openSqliteAction = QAction("&Open SQLite", self)
        self.openSqliteAction.setShortcut(QKeySequence.Open)
        self.openSqliteAction.triggered.connect(self.openSqlite)

        self.newAction = QAction("&New", self)
        self.newAction.setShortcut(QKeySequence.New)
        self.newAction.triggered.connect(self.createDb)

        self.submitAction = QAction("&Submit", self)
        self.submitAction.setShortcut(QKeySequence.Save)
        self.submitAction.triggered.connect(self.tab1.tableView.modelSubmit)

        self.refreshAction = QAction("&Refresh", self)
        self.refreshAction.setShortcut(QKeySequence.Refresh)
        self.refreshAction.triggered.connect(self.refresh)

        self.disconnectAction = QAction("&Disconnect", self)
        self.disconnectAction.setShortcut(QKeySequence.Close)
        self.disconnectAction.triggered.connect(lambda: self.disconnectedSignal.emit())

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        openMenu = fileMenu.addMenu("&Open")
        openMenu.addAction(self.openSqliteAction)
        # fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.submitAction)
        fileMenu.addAction(self.refreshAction)
        fileMenu.addAction(self.disconnectAction)

        self.connectedSignal.connect(lambda: self.setWindowTitle('BPyQSql - ' + self.dbName))
        self.disconnectedSignal.connect(lambda: self.setWindowTitle('BPyQSql'))
        self.connectedSignal.connect(lambda: self.submitAction.setEnabled(True))
        self.disconnectedSignal.connect(lambda: self.submitAction.setEnabled(False))
        self.connectedSignal.connect(lambda: self.refreshAction.setEnabled(True))
        self.disconnectedSignal.connect(lambda: self.refreshAction.setEnabled(False))
        self.connectedSignal.connect(lambda: self.disconnectAction.setEnabled(True))
        self.disconnectedSignal.connect(lambda: self.disconnectAction.setEnabled(False))

        self.disconnectedSignal.emit()
        self.show()

    def prepared(self, dbName):
        if dbName is None or dbName == '':
            self.dbName = None
            self.disconnectedSignal.emit()
        else:
            self.dbName = dbName
            self.connectedSignal.emit(self.db)

    def refresh(self):
        self.connectedSignal.emit(self.db)

    def createDb(self):
        try:
            # 调用输入框获取数据库名称
            dbText, db_action = QInputDialog.getText(self, '数据库名称', '请输入数据库名称')
            if (dbText.replace(' ', '') != '') and (db_action is True):
                print(dbText)
                # 添加一个sqlite数据库连接并打开
                db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
                db.setDatabaseName('{}.sqlite'.format(dbText))
                db.open()
                # 实例化一个查询对象
                query = QtSql.QSqlQuery()
                # 创建一个数据库表
                query.exec_("create table zmister(ID int primary key, "
                            "site_name varchar(20), site_url varchar(100))")
                # 插入三条数据
                query.exec_("insert into zmister values(1000, '州的先生', 'https://zmister.com')")
                query.exec_("insert into zmister values(1001, '百度', 'http://www.baidu.com')")
                query.exec_("insert into zmister values(1002, '腾讯', 'http://www.qq.com')")

                self.prepared(dbText)
                print('创建数据库成功')
        except Exception as e:
            print(e)
        self.connectedSignal.emit(self.db)

    def openSqlite(self):
        if self.db is not None:
            self.disconnectedSignal.emit()

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open SQLite file', '.', '*.sqlite')
        if filename.strip() == '':
            return
        self.db = DataBase("QSQLITE", name=filename)
        self.db.connection()

        if self.db.connection().isOpen():
            self.prepared(filename)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        reply = QMessageBox.question(self, 'What?', 'Sure to exit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class DataBaseView(QSplitter):
    def __init__(self, mainUI: MainUI):
        super().__init__()

        self.db = None

        self.tableListView = TableListView(mainUI)
        self.tableView = TableView(mainUI)

        self.addWidget(self.tableListView)
        self.addWidget(self.tableView)

        self.setOrientation(Qt.Horizontal)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 3)

        mainUI.connectedSignal.connect(self.updateDbView)
        mainUI.disconnectedSignal.connect(self.clear)

    def clear(self):
        self.db = None
        self.tableView.clear()
        self.tableListView.clear()

    def updateDbView(self, db: DataBase):
        self.db = db
        self.tableListView.updateDb(db)
        if self.tableView.model is not None:
            self.tableView.model.clear()
        # selectionModel will appear only after model has been set
        self.tableListView.selectionModel().selectionChanged.connect(
            lambda selected, _: self.tableView.updateTable(self.db, selected))


class TableListView(QtWidgets.QListView):
    def __init__(self, mainUI: MainUI):
        super().__init__()
        self.model = None
        self.setSelectionMode(self.SingleSelection)

    def clear(self):
        if self.model is not None:
            self.model.clear()
            self.model = None

    def updateDb(self, db: DataBase):
        self.model = QtSql.QSqlQueryModel()
        self.setModel(self.model)
        # self.model.setQuery("SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = 'test';")
        self.model.setQuery("SELECT name FROM sqlite_master WHERE type='table';",
                            db=db.connection())
        self.model.query()


class TableView(QTableView):
    def __init__(self, mainUI: MainUI):
        super().__init__()
        self.model = None
        self.mainUI = mainUI

        exportAction = QAction("Export to CSV")
        exportAction.triggered.connect(self.exportCsv)
        self.addAction(exportAction)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def clear(self):
        if self.model is not None:
            self.model.clear()
            self.model = None

    def doUpdateTable(self, db: DataBase, tableName: str):
        self.model = QtSql.QSqlTableModel(db=db.connection())
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.setModel(self.model)

        self.model.setTable(tableName)
        self.model.select()

    def updateTable(self, db: DataBase, selected: QItemSelection):
        index = selected.indexes()[0]
        tableName = selected.indexes()[0].model().data(index)
        print(tableName)
        self.doUpdateTable(db, tableName)

    def modelSubmit(self):
        try:
            ret = self.model.submitAll()
            if not ret:
                raise Exception
            self.mainUI.statusBar().showMessage("Submit success", 1000)
            print("Submit success")
        except:
            self.mainUI.statusBar().showMessage("Submit failed", 1000)
            print("Submit failed")
        # self.mainUI.refresh()

    def exportCsv(self):
        if self.model is None:
            return
        Exporter().exportCsv(self, self.model)


class Exporter():
    def exportCsv(self, parent: QWidget, model: QtCore.QAbstractTableModel):
        csvTexts = []
        rows = model.rowCount()
        cols = model.columnCount()

        headers = []
        for j in range(cols):
            headers.append(str(model.headerData(j, Qt.Horizontal)))
        csvTexts.append(','.join(headers))
        csvTexts.append('\n')

        for i in range(rows):
            rowTexts = []
            for j in range(cols):
                rowTexts.append(str(model.data(model.index(i, j))))
            csvTexts.append(','.join(rowTexts))
            csvTexts.append('\n')

        csvText = ''.join(csvTexts)

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(parent, 'Export to CSV', '.', '*.csv')
        csv = QFile(filename)
        if csv.open(csv.WriteOnly | csv.Truncate):
            csv.write(bytes(csvText, encoding='utf8'))
            csv.close()


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
        self.mainUI.statusBar().showMessage(message, 10000)
        # print(self.model.lastError().type())

    def updateQueryView(self, db: DataBase):
        self.db = db
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
