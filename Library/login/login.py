import base64


class LoginController():
    user_ticket_id = None

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

    @staticmethod
    def get_ticket_id(connection, username):
        query = """SELECT ticket_id
                        FROM reader 
                        WHERE log_email='%s';""" % username
        res = connection.connect().execute(query)
        ticket_id = [list(i) for i in res]
        return ticket_id[0][0]

