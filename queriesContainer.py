from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QLabel

from database import Database
from queryView import QueryView


class QueriesContainer(QWidget):
    statusBarMessageSignal = pyqtSignal([str, int])

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(self.tabs.South)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        self.hintLabel = QLabel(self)
        self.hintLabel.setTextFormat(Qt.RichText)
        self.hintLabel.setAlignment(Qt.AlignCenter)
        self.hintLabel.setText("""
        <table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" align="center" 
        cellspacing="2" cellpadding="0"><tr><td><p><span style=" font-size:24pt; font-weight:600; color:#6c6c6c;">%s
        </span></p></td> <td><p><span style=" font-size:24pt; font-weight:600; color:#6c6c6c;">: File</span>
        <span style=" font-size:24pt; color:#6c6c6c;"> ➡️ Add Query Tab</span></p></td></tr></table>
        """ % QKeySequence(QKeySequence.AddTab).toString(QKeySequence.NativeText))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.hintLabel)
        self.setLayout(layout)

        self.totalCount = 0
        self.queryViews = []
        self.db = None
        self.enabled = False

    def clear(self):
        for queryView in self.queryViews:
            queryView.clear()

    def updateQueryView(self, db: Database):
        self.db = db
        for queryView in self.queryViews:
            queryView.updateQueryView(db)

    def setBzEnabled(self, enabled: bool):
        self.enabled = enabled
        for queryView in self.queryViews:
            queryView.setBzEnabled(enabled)

    def newTab(self) -> QueryView:
        queryView = QueryView(self)
        self.queryViews.append(queryView)
        queryView.statusBarMessageSignal.connect(self.statusBarMessageSignal)
        if self.db is not None:
            queryView.updateQueryView(self.db)
        queryView.setBzEnabled(self.enabled)
        return queryView

    def closeTab(self, index: int):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.layout().removeWidget(self.tabs)
            self.layout().addWidget(self.hintLabel)
            self.hintLabel.show()

    def addTab(self):
        if self.tabs.count() == 0:
            self.layout().removeWidget(self.hintLabel)
            self.layout().addWidget(self.tabs)
            self.hintLabel.hide()

        queryView = self.newTab()
        self.totalCount += 1
        index = self.tabs.addTab(queryView, "Tab %d" % self.totalCount)
        self.tabs.setCurrentIndex(index)
