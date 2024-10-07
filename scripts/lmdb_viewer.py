import sys
import lmdb
import chardet
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox

class LMDBViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.open_db()

    def initUI(self):
        self.setWindowTitle('LMDB Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Key', 'Value'])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def open_db(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        db_file, _ = QFileDialog.getOpenFileName(self, "Select file LMDB", "", "All files (*)", options=options)
        if db_file:
            try:
                env = lmdb.open(db_file, subdir=False, readonly=True, lock=False)
                txn = env.begin()
                cursor = txn.cursor()
                self.load_data(cursor)
                cursor.close()
                txn.abort()
                env.close()
            except Exception as e:
                QMessageBox.critical(None, 'Error', f'The LMDB database could not be opened: {e}')
                sys.exit(1)
        else:
            QMessageBox.warning(None, 'Warning', 'File not selected.')
            sys.exit(0)

    def load_data(self, cursor):
        row = 0
        for key, value in cursor:
            self.table.insertRow(row)

            try:
                key_enc = chardet.detect(key)['encoding'] or 'utf-8'
                key_str = key.decode(key_enc, errors='replace')
            except Exception:
                key_str = key.hex()

            try:
                value_enc = chardet.detect(value)['encoding'] or 'utf-8'
                value_str = value.decode(value_enc, errors='replace')
            except Exception:
                value_str = value.hex()

            key_item = QTableWidgetItem(key_str)
            value_item = QTableWidgetItem(value_str)
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, value_item)
            row += 1

def main():
    app = QApplication(sys.argv)
    try:
        viewer = LMDBViewer()
        viewer.show()
    except Exception as e:
        QMessageBox.critical(None, 'Critical error', f'An error occurred when opening the program: {e}')
        sys.exit(1)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()