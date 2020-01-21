from abc import ABC, abstractmethod
from database import Database


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
