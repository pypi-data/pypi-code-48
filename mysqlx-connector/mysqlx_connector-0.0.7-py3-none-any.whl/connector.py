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


class Table(Database, ABC):
    """Table class for mysql connector.

    Abstract base class for table in mysql using x protocol.
    """

    def __init__(self, table_name: str, db_name: str, conn_options=None):
        super().__init__(db_name, conn_options)
        self._table_name = table_name

    def __enter__(self):
        super().__enter__()
        self._table = self._database.get_table(self._table_name)
        return self

    def __repr__(self):
        return f'Table object for {self._table_name} in {self._database_name}'

    @staticmethod
    def parse_results(results):
        """Parses rowResult object.

        Parses rowResult object and yields it row by row.
        """
        for result in results.fetch_all():
            row = dict()
            for column in results.columns:
                cell = result[column.column_name]
                # Check if column is tinyint(1) aka boolean
                if column.type == 2 and column.length == 1:
                    cell = bool(cell)
                row[column.column_name] = cell
            yield row
