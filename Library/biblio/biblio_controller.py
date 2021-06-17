import pandas as pd

from pandas_model.pandas_model import pandasModel
from datetime import datetime


class BiblioController:

    @staticmethod
    def load_biblio_data(connection):
        query = """ SELECT * FROM BOOK"""
        df_res = pd.read_sql(query, connection)
        df_res.rename(columns={'isbn': 'ISBN','title': 'Назва','city': 'Місто', 'publisher': 'Видавництво', 'year_publication': 'Рік видання',
                               'pages': 'Сторінок', 'price': 'Ціна', 'copies_num': 'Примірників'}, inplace=True)
        p_model = pandasModel(df_res)
        return p_model

    @staticmethod
    def load_inven_data(connection):
        query = """ SELECT inven_id, shelf, copy.isbn, book.title 
        FROM copy INNER JOIN book ON copy.isbn = book.isbn"""
        df_res = pd.read_sql(query, connection)
        df_res.rename(columns={'inven_id': 'Інвен номер', 'shelf': 'Полиця', 'isbn': 'ISBN', 'title': 'Назва'}, inplace=True)
        df_res.sort_values(by=['Інвен номер'])
        p_model = pandasModel(df_res)
        return p_model

    @staticmethod
    def load_reader_copy_data(connection):
        query = """ SELECT * FROM reader_copy"""
        df_res = pd.read_sql(query, connection)
        df_res.rename(columns={'ticket_id': 'Номер читач', 'inven_id': 'Інвен номер', 'issue_date': 'Дата видачі', 'expected_return_date': 'Очікувана дата', 'actual_return_date': 'Актуальна дата'}, inplace=True)
        df_res = df_res.loc[:, df_res.columns != 'ticket_id']
        p_model = pandasModel(df_res)
        return p_model

    @staticmethod
    def add_book_to_db(connection, fields_list, city, sphere):
        query = """INSERT INTO book 
        VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', %s)""" % (fields_list[0].text(), fields_list[1].text(), city, fields_list[2].text(), fields_list[3].text(),
                                                     fields_list[4].text(), fields_list[5].text(), fields_list[6].text())
        connection.connect().execute(query)

        query = """SELECT surname 
                FROM authors"""
        res = connection.connect().execute(query)
        aut_lst = [list(i) for i in res]
        authors = [aut_lst[i][0] for i in range(0, len(aut_lst))]

        author_strip = fields_list[7].text().split()
        if author_strip[0] not in authors:
            query = """INSERT INTO authors 
                   VALUE('%s', '%s')""" % (author_strip[0], author_strip[1])
            connection.connect().execute(query)

        query = """INSERT INTO book_authors 
        VALUE('%s', '%s', '%s')""" % (author_strip[0], author_strip[1], fields_list[0].text())
        connection.connect().execute(query)

        query = """SELECT sphere_id 
              FROM catalog
              WHERE sphere_name = '%s' """ % sphere
        res = connection.connect().execute(query)
        isbns_lst = [list(i) for i in res]
        isbns = [isbns_lst[i][0] for i in range(0, len(isbns_lst))]

        query = """INSERT INTO catalog_book
                             VALUES('%s', '%s')""" % (isbns[0], fields_list[0].text())
        connection.connect().execute(query)

    @staticmethod
    def add_book_to_inven(connection, inven_id, shelf, isbn, sphere):
        query = """INSERT INTO copy (inven_id, shelf, isbn)
               VALUES(%s, %s, '%s')""" % (inven_id, shelf, isbn)
        connection.connect().execute(query)

    @staticmethod
    def add_reader_copy_record(connection, inven_id, ticket_id, expected_date):
        today = datetime.today().strftime('%Y-%m-%d')
        query = """INSERT INTO reader_copy (ticket_id, inven_id, issue_date, expected_return_date)
                   VALUES(%s, %s, '%s', '%s')""" % (ticket_id, inven_id, today, expected_date)
        connection.connect().execute(query)

    @staticmethod
    def check_isbn_ispresent(connection, isbn):
        query = """SELECT isbn FROM BOOK"""
        res = connection.connect().execute(query)
        isbns_lst = [list(i) for i in res]
        isbns = [isbns_lst[i][0] for i in range(0, len(isbns_lst))]
        return isbn in isbns

    @staticmethod
    def check_inven_ispresent(connection, inven_id):
        query = """SELECT inven_id FROM copy"""
        res = connection.connect().execute(query)
        invens_lst = [list(i) for i in res]
        invens = [str(invens_lst[i][0]) for i in range(0, len(invens_lst))]
        return inven_id in invens

    @staticmethod
    def get_all_isbns(connection):
        query = """SELECT isbn FROM book"""
        result = connection.connect().execute(query)
        lst_isbns = [list(i) for i in result]
        res = [lst_isbns[i][0] for i in range(0, len(lst_isbns))]
        return res

    @staticmethod
    def get_all_copies(connection):
        query = """SELECT inven_id FROM copy"""
        result = connection.connect().execute(query)
        lst_isbns = [list(i) for i in result]
        res = [str(lst_isbns[i][0]) for i in range(0, len(lst_isbns))]
        return res

    @staticmethod
    def get_all_readers(connection):
        query = """SELECT ticket_id FROM reader"""
        result = connection.connect().execute(query)
        lst_isbns = [list(i) for i in result]
        res = [str(lst_isbns[i][0]) for i in range(0, len(lst_isbns))]
        return res

    @staticmethod
    def get_all_spheres(connection):
        query = """SELECT sphere_name FROM catalog"""
        result = connection.connect().execute(query)
        lst_isbns = [list(i) for i in result]
        res = [str(lst_isbns[i][0]) for i in range(0, len(lst_isbns))]
        return res
