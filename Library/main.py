import sys
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLineEdit, QWidget, QGridLayout, QHeaderView
from PyQt5 import QtWidgets

from biblio.biblio_controller import BiblioController
from database.db_connection import Database
from login.login import LoginController
from reader.readerview import ReaderView
from ui_main import Ui_MainWindow


class MainWindow(QMainWindow):
    connection = None
    curr_user = None

    def __init__(self, connection):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)
        self.connection = connection
        self.ui.username.setText("biblio@test.com")
        self.ui.password.setText("2u12345")

        self.ui.login.clicked.connect(self.check_user_creds)

        #Biblio page
        self.ui.tabWidget.setCurrentWidget(self.ui.book_registration)
        self.ui.city_input.addItems(['*','Київ', 'Харків', 'Одеса', 'Дніпро', 'Донецьк', 'Запоріжжя', 'Львів', 'Вінниця', 'Полтава', 'Чернігів'])
        self.ui.isbn_input_inv.addItems(['*'] + BiblioController.get_all_isbns(self.connection))
        self.ui.book_sphere.addItems(['*'] + BiblioController.get_all_spheres(self.connection))
        self.ui.shelf_input.addItems(['*'] + sorted([str(i) for i in range(1, 11)]))
        self.ui.invenId_give.addItems(['*'] + sorted(BiblioController.get_all_copies(self.connection)))
        self.ui.ticketId_give.addItems(['*'] + sorted(BiblioController.get_all_readers(self.connection)))


        self.ui.add_book_btn.clicked.connect(self.add_book)
        self.ui.add_author_btn.clicked.connect(self.add_author_input)
        self.ui.saveInventory.clicked.connect(self.add_book_to_inven)
        self.ui.save_give.clicked.connect(self.add_reader_copy_record)

        self.ui.inven_db_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.ui.reader_copy_view.horizontalHeader().setStretchLastSection(True)
        self.ui.reader_copy_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.reader_view = None
        self.show()

    def check_user_creds(self):
        user_present = LoginController.checkUser(self.connection, self.ui.username.text(), self.ui.password.text())
        login_status = QMessageBox()
        if user_present == 'reader':
            login_status.buttonClicked.connect(self.reader_window)
            self.curr_user = LoginController.get_ticket_id(self.connection, self.ui.username.text())
            login_status.setText('Успіх Читач')
        elif user_present == 'admin':
            login_status.setText('Успіх Адміністратор')
        elif user_present == 'biblio':
            login_status.setText('Успіх Бібліотекар')
            login_status.buttonClicked.connect(self.biblio_window)
        else:
            login_status.setText('Спробуйте ще раз')

        login_status.exec_()

    #BIBLIOTEKAR
    def add_book(self):
        if self.check_book_input() and not BiblioController.check_isbn_ispresent(self.connection, self.ui.isbn_input.text()):
            BiblioController.add_book_to_db(self.connection, self.get_all_inputs_reg(), self.ui.city_input.currentText(), self.ui.book_sphere.currentText())
            updated_model1 = BiblioController.load_biblio_data(self.connection)
            self.ui.book_table_view.setModel(updated_model1)
            self.reload_book_reg()
            self.ui.isbn_input_inv.clear()
            self.ui.isbn_input_inv.addItems(['*'] + BiblioController.get_all_isbns(self.connection))
        else:
            msg = QMessageBox()
            msg.setText('Дублювання ISBN')
            msg.exec_()

    def check_book_input(self):
        flag = True
        inputs_list = self.get_all_inputs_reg()
        for i in inputs_list:
            if i.text() == '':
                flag = False
                i.setStyleSheet('border: 1px solid red;')
        return flag

    def check_book_inv_input(self):
        flag = True
        if self.ui.isbn_input_inv.currentText() == '*':
            flag = False
            self.ui.isbn_input_inv.setStyleSheet('border: 1px solid red;')
        if self.ui.invenId.text()  == '':
            flag = False
            self.ui.invenId.setStyleSheet('border: 1px solid red;')
        if self.ui.shelf_input.currentText() == '*':
            flag = False
            self.ui.shelf_input.setStyleSheet('border: 1px solid red;')
        return flag


    def get_all_inputs_reg(self):
        return [self.ui.isbn_input, self.ui.title_input, self.ui.publisher_input, self.ui.year_input,
                       self.ui.pages_input, self.ui.price_input, self.ui.copies_count_input,
                       self.ui.author_input]


    def add_author_input(self):
        # line = QLineEdit()
        # self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        # grid = QGridLayout(self.ui.scrollAreaWidgetContents)
        # self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)
        # grid.addWidget(line, 0, 0)
        pass

    def add_book_to_inven(self):
        if self.check_book_inv_input() and not BiblioController.check_inven_ispresent(self.connection, self.ui.invenId.text()):
            inven_id = self.ui.invenId.text()
            isbn = self.ui.isbn_input_inv.currentText()
            shelf = self.ui.shelf_input.currentText()
            sphere = self.ui.book_sphere.currentText()
            BiblioController.add_book_to_inven(self.connection, inven_id, shelf, isbn, sphere)
            updated_model = BiblioController.load_inven_data(self.connection)
            self.ui.inven_db_view.setModel(updated_model)
            self.reload_book_inv()

        elif not self.check_book_inv_input():
            msg = QMessageBox()
            msg.setText('Заповніть поля')
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setText('Інвентарний номер вже існує')
            msg.exec_()

    def add_reader_copy_record(self):
        if self.ui.expected_date.date() < datetime.today().date():
            msg = QMessageBox()
            msg.setText('Неправильна дата')
            msg.exec_()
            return
        inven_id = self.ui.invenId_give.currentText()
        ticket_id = self.ui.ticketId_give.currentText()
        expected_date = self.ui.expected_date.date()
        expected_date = expected_date.toPyDate()
        BiblioController.add_reader_copy_record(self.connection, inven_id, ticket_id, expected_date)
        updated_model = BiblioController.load_reader_copy_data(self.connection)
        self.ui.reader_copy_view.setModel(updated_model)
        self.reload_reader_copy()

    def biblio_window(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
        biblio_db_model = BiblioController.load_biblio_data(self.connection)
        inven_db_model = BiblioController.load_inven_data(self.connection)
        give_db_model = BiblioController.load_reader_copy_data(self.connection)
        self.ui.book_table_view.setModel(biblio_db_model)
        self.ui.inven_db_view.setModel(inven_db_model)
        self.ui.reader_copy_view.setModel(give_db_model)


    def reader_window(self):
        self.reader_view = ReaderView(self.curr_user)
        self.reader_view.show()
        self.reload_login()

    def reload_login(self):
        self.ui.username.clear()
        self.ui.password.clear()
        self.showMinimized()

    def reload_book_reg(self):
        for i in self.get_all_inputs_reg():
            i.setText('')
        self.ui.city_input.setCurrentText('*')

    def reload_book_inv(self):
        self.ui.isbn_input_inv.setCurrentText('*')
        self.ui.invenId.setText('')
        self.ui.shelf_input.setCurrentText('*')
        self.ui.book_sphere.setCurrentText('*')

    def reload_reader_copy(self):
        self.ui.ticketId_give.setCurrentText('*')
        self.ui.invenId_give.setCurrentText('*')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_connection = Database.connect_to_db()
    window = MainWindow(db_connection)
    window.connection = db_connection
    sys.exit(app.exec_())