import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHeaderView, QMessageBox, QCalendarWidget, QWidget
import pandas as pd
from datetime import datetime

from database.db_connection import Database
from pandas_model.pandas_model import pandasModel


class ReaderView(QWidget):
    connection = None
    res_df = None
    res_title = None
    ticket_id = None

    def __init__(self, ticket_id):
        super().__init__()
        self.connection = Database.connect_to_db()
        self.ticket_id = ticket_id
        self.setupUi(self)
        self.load_all_data()

    def load_all_data(self):
        query = """SELECT title, publisher, year_publication, authors.surname, authors.initials
                                  FROM (authors INNER JOIN book_authors ON authors.surname = book_authors.author_surname)
                                  INNER JOIN book ON book_authors.book_isbn = book.isbn
                                  INNER JOIN catalog_book ON book.isbn = catalog_book.isbn 
                                  ORDER BY title"""
        df_res = pd.read_sql(query, self.connection)
        df_res.rename(columns={'title': 'Назва', 'publisher': 'Видавництво', 'year_publication': 'Рік видання', 'surname': 'Прізвище', 'initials': 'Ініціали'}, inplace=True)
        self.res_df = df_res
        p_model = pandasModel(self.res_df)
        self.db_view.setModel(p_model)

    def load_data_params(self, title='', author='', sphere=''):
        if author == '*' and sphere == '*':
            self.load_all_data()
            return

        query = """SELECT title, publisher, year_publication, authors.surname, authors.initials
                                  FROM (authors INNER JOIN book_authors ON authors.surname = book_authors.author_surname)
                                  INNER JOIN book ON book_authors.book_isbn = book.isbn
                                  INNER JOIN catalog_book ON book.isbn = catalog_book.isbn
                                  WHERE
                                  """

        if title != '':
            query += """ book.title = '%s'""" % title
            if author != '*':
                query += 'AND'

        if author != '*':
            query += """ authors.surname = '%s'""" % author
            if sphere != '*':
                query += ' AND'

        if sphere != '*':
            query += """ catalog_book.sphere_id IN (SELECT sphere_id
                                           FROM catalog
                                           WHERE sphere_name = '%s');""" % sphere
        df_res = pd.read_sql(query, self.connection)
        df_res.rename(columns={'title': 'Назва', 'publisher': 'Видавництво', 'year_publication': 'Рік видання', 'surname': 'Прізвище', 'initials': 'Ініціали'}, inplace=True)
        self.res_df = df_res
        p_model = pandasModel(self.res_df)
        self.db_view.setModel(p_model)

    def enter_clicked(self):
        title = str(self.lineEdit.text())
        author = str(self.authorsBox.currentText())
        sphere = str(self.sphereBox.currentText())
        self.load_data_params(title, author, sphere)

    def get_all_authors(self):
        query = "SELECT surname FROM authors"
        result = self.connection.connect().execute(query)
        lst_authors = [list(i) for i in result]
        res = [lst_authors[i][0] for i in range(0, len(lst_authors))]
        return res

    def get_all_spheres(self):
        query = "SELECT sphere_name FROM catalog"
        result = self.connection.connect().execute(query)
        lst_spheres = [list(i) for i in result]
        res = [lst_spheres[i][0] for i in range(0, len(lst_spheres))]
        return res

    def check_copy(self, title):
        query = """SELECT copy.inven_id
                    FROM copy INNER JOIN book ON copy.isbn = book.isbn 
                    WHERE book.title = '%s' AND EXISTS 

                    (SELECT inven_id 
                    FROM reader_copy
                    WHERE copy.inven_id = inven_id AND expected_return_date < CURDATE() AND actual_return_date IS NOT NULL);""" % title
        res = self.connection.connect().execute(query)
        copies = [list(i) for i in res]
        return [copies[i][0] for i in range(0, len(copies))]

    def check_copy_return_date(self, title):
        query = """SELECT copy.inven_id, reader_copy.expected_return_date 
        FROM (reader_copy INNER JOIN copy ON reader_copy.inven_id = copy.inven_id) INNER JOIN book ON copy.isbn = book.isbn 
        WHERE book.title = '%s' AND reader_copy.expected_return_date > CURDATE();""" % title
        res = self.connection.connect().execute(query)
        dates = [list(i) for i in res]
        return [{dates[i][0]: dates[i][1].strftime('%Y-%m-%d')} for i in range(0, len(dates))]

    def cell_left_click(self, item):
        msg = QMessageBox()
        msg.setWindowTitle('Наявність примірника книги')
        self.res_title = self.res_df.iloc[item.row(), 0]
        copies = self.check_copy(self.res_title)
        msg_text = 'Назва: ' + self.res_title
        if len(copies) != 0:
            msg_text += '\nДоступні примірники: %s' % copies
            msg.addButton(self.tr("Взяти книгу"), QMessageBox.ActionRole)
            msg.buttonClicked.connect(self.select_date)
        else:
            msg_text += '\nНаявність: Немає доступних примірників'
            dates_list = self.check_copy_return_date(self.res_title)
            msg_text += '\n\nБудуть доступні:\n'
            for i in range(len(dates_list)):
                key, value = list(dates_list[i].items())[0]
                dates_text = 'Номер: ' + str(key) + '  Дата: ' + str(value) + '\n'
                msg_text += dates_text
        msg.setText(msg_text)
        msg.exec_()

    def select_date(self):
        self.dateSelector.setVisible(True)
        self.setDateBtn.setVisible(True)

    def take_book(self):
        date_return = self.dateSelector.selectedDate().toPyDate()
        today = datetime.today().strftime('%Y-%m-%d')
        copy_inven_id = self.check_copy(self.res_title)[0]
        query = """INSERT INTO reader_copy (ticket_id, inven_id, issue_date, expected_return_date) 
        VALUES(%s, %s, '%s', '%s')""" % (self.ticket_id, copy_inven_id, today, date_return)
        self.connection.connect().execute(query)
        self.dateSelector.setVisible(False)
        self.setDateBtn.setVisible(False)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1300, 720)
        self.db_widget = QtWidgets.QWidget(Form)
        self.db_widget.setGeometry(QtCore.QRect(390, 10, 890, 680))
        self.db_widget.setStyleSheet("border: 10px;\n"
                                     "border-color: rgb(0, 0, 0);\n"
                                     "background-color: rgb(255, 255, 255);")
        self.db_widget.setObjectName("db_widget")

        self.db_view = QtWidgets.QTableView(self.db_widget)
        self.db_view.setGeometry(QtCore.QRect(5, 11, 890, 651))
        self.db_view.setObjectName("db_view")
        self.db_view.horizontalHeader().setStretchLastSection(True)
        self.db_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.db_view.setObjectName("tableWidget")
        self.db_view.clicked.connect(self.cell_left_click)

        self.verticalLayoutWidget = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 371, 281))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.authorsBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.authorsBox.addItem("*")
        self.authorsBox.addItems(self.get_all_authors())
        self.authorsBox.setObjectName("authorsBox")
        self.gridLayout.addWidget(self.authorsBox, 1, 1, 1, 1)

        self.sphereBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.sphereBox.addItem("*")
        self.sphereBox.addItems(self.get_all_spheres())
        self.sphereBox.setObjectName("sphereBox")
        self.gridLayout.addWidget(self.sphereBox, 2, 1, 1, 1)

        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setStyleSheet("font: 20pt \"Arial\";")
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setStyleSheet("font: 20pt \"Arial\";")
        self.label.setObjectName("label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setObjectName("authorInput")

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setStyleSheet("font: 20pt \"MS Shell Dlg 2\";")
        self.label_2.setObjectName("label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.verticalLayout.addLayout(self.gridLayout)

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(140, 340, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.enter_clicked)

        self.dateSelector = QCalendarWidget(Form)
        self.dateSelector.setGridVisible(True)
        self.dateSelector.setFixedWidth(350)
        self.dateSelector.move(20,420)
        self.dateSelector.setVisible(False)

        self.setDateBtn = QtWidgets.QPushButton(Form)
        self.setDateBtn.setGeometry(QtCore.QRect(140, 340, 93, 28))
        self.setDateBtn.setObjectName("setDateButton")
        self.setDateBtn.clicked.connect(self.enter_clicked)
        self.setDateBtn.setFixedWidth(250)
        self.setDateBtn.move(60, 675)
        self.setDateBtn.setVisible(False)
        self.setDateBtn.clicked.connect(self.take_book)

        self.retranslate_ui(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslate_ui(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_3.setText(_translate("Form", "Сфера"))
        self.label.setText(_translate("Form", "Назва"))
        self.label_2.setText(_translate("Form", "Автори"))
        self.pushButton.setText(_translate("Form", "Пошук"))
        self.setDateBtn.setText(_translate("Form", "Підтвердити дату повернення"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = ReaderView()
    db_connection = Database.connect_to_db()
    ui.connection = db_connection
    ui.setupUi(Form)
    ui.load_all_data()
    Form.show()
    sys.exit(app.exec_())