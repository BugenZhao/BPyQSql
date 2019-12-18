from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtWidgets import QWidget


class Exporter:
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
