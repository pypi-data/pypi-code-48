import mysqlx
from os import environ
from abc import ABC, abstractmethod


class Database(ABC):
    """ Mysql database connector.

    Mysql database connector that supports the X protocol.
    """

    def __init__(self, db_name, conn_options=None):
        self._database_name = db_name

        self._client = mysqlx.get_client(
            {
                'host': environ['HOST'],
                'port': environ['PORT'],
                'user': environ['USER'],
                'password': environ['PASSWORD']
            },
            conn_options if conn_options is not None else {}
        )

    def __enter__(self):
        self._session = self._client.get_session()
        self._database = self._session.get_schema(self._database_name)
        return self

    def __exit__(self, exception_type, execption_value, traceback):
        self._session.close()

    def __repr__(self):
        return f'A database object for {self._database_name}'

    def connect(self):
        """Connect to database.

        Connect to database using provided environment variables. I
        recommend not using this as you can use the with statement.
        If you happen to use this, remember to close the session with
        the `close()` method.
        """
        return self._client.get_session()
