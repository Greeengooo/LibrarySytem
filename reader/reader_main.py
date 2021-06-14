from aifc import Error
from sqlalchemy import create_engine
from sqlalchemy import engine
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHeaderView
import pandas as pd
from reader.pandas_model import pandasModel


class Search(object):
    connection = None

    def load_data(self, age):
        query = """SELECT ticket_id, initials FROM reader WHERE ticket_id IN (SELECT ticket_id FROM reader WHERE 
        TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) = %s AND ticket_id IN (SELECT ticket_id FROM copy WHERE isbn IN (
        SELECT isbn FROM book WHERE year_publication = 2008 AND isbn IN (SELECT isbn FROM book_authors WHERE 
        author_surname = "Антоненко")) AND (YEAR(issue_date) = 2020 AND MONTH(issue_date) = 10) AND (YEAR(
        return_date) = 2021 AND MONTH(return_date) = 4))); """ % age
        df_res = pd.read_sql(query, self.connection)
        p_model = pandasModel(df_res)
        self.db_view.setModel(p_model)

    def load_all_data(self):
        query = """SELECT title, publisher, year_publication, authors.surname, authors.initials
                                  FROM (authors INNER JOIN book_authors ON authors.surname = book_authors.author_surname)
                                  INNER JOIN book ON book_authors.book_isbn = book.isbn
                                  INNER JOIN catalog_book ON book.isbn = catalog_book.isbn """
        df_res = pd.read_sql(query, self.connection)
        p_model = pandasModel(df_res)
        self.db_view.setModel(p_model)

    def load_data_params(self, title='', author='', sphere=''):
        query = """SELECT title, publisher, year_publication, authors.surname, authors.initials
                                  FROM (authors INNER JOIN book_authors ON authors.surname = book_authors.author_surname)
                                  INNER JOIN book ON book_authors.book_isbn = book.isbn
                                  INNER JOIN catalog_book ON book.isbn = catalog_book.isbn
                                  WHERE"""
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
        p_model = pandasModel(df_res)
        self.db_view.setModel(p_model)

    def connect_to_db(self):
        try:
            self.connection = create_engine(engine.url.URL.create(
                drivername='mysql+pymysql',
                username='root',
                password='12345',
                database='library', ))
        except Error as err:
            print(f"Error: '{err}'")

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

    def init_ui(self, Form):
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

        self.retranslate_ui(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslate_ui(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_3.setText(_translate("Form", "Sphere"))
        self.label.setText(_translate("Form", "Title"))
        self.label_2.setText(_translate("Form", "Authors"))
        self.pushButton.setText(_translate("Form", "Search"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Search()
    ui.connect_to_db()
    ui.init_ui(Form)
    #ui.load_all_data()
    ui.load_data(18)
    Form.show()
    sys.exit(app.exec_())