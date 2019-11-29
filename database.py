from PyQt5 import QtSql
from PyQt5.QtSql import QSqlDatabase


class DataBase:
    def __init__(self, type: str, name: str = '', info=None):
        if info is None:
            info = {}
        if name == '':
            name = info['host']

        self.db = None
        self.type = type
        self.info = info
        self.name = name
        if "port" in info:
            self.name += ':%d' % self.info['port']

        self.connName = str(hash(type + name))

    def connection(self) -> QSqlDatabase:
        if self.db is not None:
            return self.db

        db = QtSql.QSqlDatabase.addDatabase(self.type, self.connName)
        if self.type == 'QSQLITE':
            db.setDatabaseName(self.name)
        elif self.type == 'QMYSQL' or self.type == 'QPSQL':
            db.setHostName(self.info['host'])
            db.setPort(self.info['port'])
            db.setUserName(self.info['user'])
            db.setPassword(self.info['pswd'])
            db.setDatabaseName(self.info['dbNm'])

        db.open()
        self.db = db
        return self.db
