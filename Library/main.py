import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from database.db_connection import Database
from login.login import LoginController
from reader.readerview import ReaderView
from ui_main import Ui_MainWindow


class MainWindow(QMainWindow):
    connection = None

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)
        self.ui.login.clicked.connect(self.check_user_creds)
        self.reader_view = None
        self.show()

    def check_user_creds(self):
        user_present = LoginController.checkUser(self.connection, self.ui.username.text(), self.ui.password.text())
        login_status = QMessageBox()
        if user_present == 'reader':
            login_status.buttonClicked.connect(self.reader_window)
            login_status.setText('Успіх Читач')
        elif user_present == 'admin':
            login_status.setText('Успіх Адміністратор')
        elif user_present == 'biblio':
            login_status.setText('Успіх Бібліотекар')
        else:
            login_status.setText('Спробуйте ще раз')

        login_status.exec_()

    def reader_window(self):
        self.reader_view = ReaderView()
        self.reader_view.show()
        self.reload_login()

    def reload_login(self):
        self.ui.username.clear()
        self.ui.password.clear()
        self.showMinimized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    db_connection = Database.connect_to_db()
    window.connection = db_connection
    sys.exit(app.exec_())