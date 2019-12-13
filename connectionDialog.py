from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QPushButton, QGridLayout, QLabel, QLineEdit, QDialogButtonBox, QDialog

from database import Database


class ConnectionDialog(QDialog):
    def __init__(self, type: str):
        super().__init__()
        self.type = type

        hostLabel = QLabel('Server name:')
        portLabel = QLabel('Server port:')
        userLabel = QLabel('Username:')
        pswdLabel = QLabel('Password:')
        dbNmLabel = QLabel('Database:')

        self.hostEdit = QLineEdit('localhost')
        self.portEdit = QLineEdit()
        self.portEdit.setValidator(QIntValidator(1, 65535, self))
        self.userEdit = QLineEdit()
        self.pswdEdit = QLineEdit()
        self.pswdEdit.setEchoMode(self.pswdEdit.Password)
        self.dbNmEdit = QLineEdit()

        hostLabel.setBuddy(self.hostEdit)
        portLabel.setBuddy(self.portEdit)
        userLabel.setBuddy(self.userEdit)
        pswdLabel.setBuddy(self.pswdEdit)
        dbNmLabel.setBuddy(self.dbNmEdit)

        self.connectBtn = QPushButton('Connect')
        self.connectBtn.setDefault(True)
        cancelBtn = QPushButton('Cancel')
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.connectBtn, buttonBox.ActionRole)
        buttonBox.addButton(cancelBtn, buttonBox.RejectRole)

        layout = QGridLayout()
        layout.addWidget(hostLabel, 0, 0)
        layout.addWidget(self.hostEdit, 0, 1)
        layout.addWidget(portLabel, 1, 0)
        layout.addWidget(self.portEdit, 1, 1, )
        layout.addWidget(userLabel, 2, 0)
        layout.addWidget(self.userEdit, 2, 1)
        layout.addWidget(pswdLabel, 3, 0)
        layout.addWidget(self.pswdEdit, 3, 1)
        layout.addWidget(dbNmLabel, 4, 0)
        layout.addWidget(self.dbNmEdit, 4, 1)
        layout.addWidget(buttonBox, 6, 1)
        self.setLayout(layout)

        self.userEdit.setFocus()

        cancelBtn.clicked.connect(self.close)
        self.connectBtn.clicked.connect(self.connect)

        if type == 'QPSQL':
            self.setWindowTitle('Connect to PostgreSQL')
            self.portEdit.setText('5432')
            self.userEdit.setText('postgres')
            self.dbNmEdit.setText('postgres')
        elif type == 'QMYSQL':
            self.setWindowTitle('Connect to MySQL')
            self.portEdit.setText('3306')

        self.database = None

    def connect(self):
        self.database = Database(self.type, info={
            'host': self.hostEdit.text(),
            'port': int(self.portEdit.text()),
            'user': self.userEdit.text(),
            'pswd': self.pswdEdit.text(),
            'dbNm': self.dbNmEdit.text()
        })
        self.close()

    def getDatabase(self) -> Database:
        return self.database
