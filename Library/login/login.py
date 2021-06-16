import base64


class LoginController():

    @staticmethod
    def checkUser(connection, username, password):
        enc_pass = base64.b64encode(password.encode("utf-8")).decode('utf-8')
        query = """SELECT *
        FROM reader 
        WHERE log_email='%s' AND log_password = '%s';""" % (username, enc_pass)
        res = connection.connect().execute(query)
        user_reader = [list(i) for i in res]
        if len(user_reader) != 0:
            return 'reader'

        query = """SELECT empl_position
                FROM employee 
                WHERE log_email='%s' AND log_password = '%s';""" % (username, enc_pass)
        res = connection.connect().execute(query)
        user_admin_biblio = [list(i) for i in res]
        if len(user_admin_biblio) == 0:
            return 0
        elif user_admin_biblio[0][0] == 'Адміністратор':
            return 'admin'
        elif user_admin_biblio[0][0] == 'Бібліотекар':
            return 'biblio'


