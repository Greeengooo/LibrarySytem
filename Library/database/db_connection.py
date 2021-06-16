from aifc import Error

from sqlalchemy import create_engine
from sqlalchemy import engine


class Database(object):

    @staticmethod
    def connect_to_db():
        connection = None
        try:
            connection = create_engine(engine.url.URL.create(
                drivername='mysql+pymysql',
                username='root',
                password='12345',
                database='library', ))
            return connection
        except Error as err:
            print(f"Error: '{err}'")
        return connection