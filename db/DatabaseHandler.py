import logging
from DataType import DataType

from MySQLdb.cursors import Cursor
from MySQLdb import Connection
from MySQLdb import Connect
from util.Repeat import repeat

logger = logging.getLogger("Database Handler")
logging.basicConfig(level=logging.DEBUG)

"""
TODO -> Comments
"""
DB_HOST = ""
DB_USER = ""
DB_PASSWORD = ""
DB_DATABASE = ""


class DatabaseHandler:
    def __init__(self):
        self.connect()

    @staticmethod
    def with_commit(func):
        def inner(self, *args, **kwargs):
            if kwargs.get("with_commit", True):
                self.commit()
            return func(self, *args, **kwargs)

        return inner

    def connect(self):
        """
        Connects | Reconnects to the database
        """
        if not hasattr(self, "cxn") or not hasattr(self, "cur"):
            self.cxn: Connection = Connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            )
            self.cur: Cursor = self.cxn.cursor(cursorclass=Cursor)
        else:
            logger.warning("Reconnecting")
            self.close(log=False)

            self.connect()
            logger.info("Successfully reconnected")

    @with_commit
    def close(self, log: bool = True):
        """
        Closes the database connection

        Args:
            log (bool, optional): Log events to logger. Defaults to True.
        """
        try:
            if log:
                logger.warning("Closing connection")
            self.cur.close()
            self.cxn.close()

            delattr(self, "cur")
            delattr(self, "cxn")
            if log:
                logger.info("Successfully closed")

        except Exception:
            logger.critical("Failed to close connection")

    def commit(self):
        """
        Commits to the db
        """
        logger.debug("Committing")
        self.cxn.commit()

    def _get_data(self, data_type: DataType, command, values):
        """
        Gets data from the db dependent on the command and values and
        returns an output based on the data type

        Args:
            data_type (DataType): Data type
            command (str): SQL command
            values (tuple): Values for command substitution

        Raises:

        Returns:
            str: Database output
        """
        self.execute(command, values)
        return data_type.get_data(self.cur)

    def record(self, command, *values):
        """
        Returns a single db row

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            tuple: Single row command output
        """
        return self._get_data(DataType.RECORD, command, values)

    def records(self, command, *values):
        """
        Returns all db rows

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            list(tuple): All command output rows
        """
        return self._get_data(DataType.RECORDS, command, values)

    def column(self, command, *values):
        """
        Returns a column of data.
        NOTE: A column must be specified

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            tuple: Single column command output
        """
        return self._get_data(DataType.COLUMN, command, values)

    def count(self, command, *values):
        """
        Returns the first value in the first row of data
        Used to get the COUNT value


        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            int: Count output
        """
        return self._get_data(DataType.COUNT, command, values)

    def last_row_id(self):
        """
        Retrieves the row ID of the most
        recent cursor command

        Returns:
            int: Row ID
        """
        return self.cur.lastrowid

    def is_in_db(self, value, col, table: str) -> tuple:
        """
        Checks if a value is in a database table and column

        Args:
            value (str): Value to look for
            col (str): Column to search
            table (Table): Table to search

        Returns:
            list[tuple]: The first found record if present
            None: If no record is present
        """
        # TODO -> Explain why this is fine
        command = f"SELECT * FROM {table} WHERE {col} = ?"
        return self.record(command, value)

    @with_commit
    def insert(
            self,
            table: str,
            cols: list[str] | set[str],
            data: tuple,
            with_commit: bool = True
    ):
        """
        Inserts data into the database

        Args:
            table (Table): Db table
            cols (list(str) | set(str)): List of column names
            data (tuple): Data to insert
            with_commit (bool, optional): Should a commit occur after this insertion. Defaults to True.
        """
        table_name = table
        cols_str = ",".join(cols)
        data_str = ",".join(["?" for _ in data])

        # TODO -> Explain why this is also fine
        self.execute(
            f"INSERT INTO {table_name} ({cols_str}) VALUES ({data_str})",
            *data
        )

    @repeat(retries=3)
    def execute(self, command, *values):
        """
        Executes a database command

        Args:
            command (str): SQL command
        Raises:
            LookupError: If the max retries limit has exceeded
        """
        # Removes nested tuples
        # TODO -> Rewrite this 2 year old dogshit code lol
        if len(values) == 1:
            values = values[0]

        values = values if values != ((),) else None
        try:
            return self.cur.execute(command, values)
        except Exception as e:
            self.connect()
            raise e

    @repeat(retries=3)
    def multiexec(self, command, valueset):
        """
        Executes a database command multiple times using a valueset

        Args:
            command (str): SQL command
            valueset (set(tuple)): Set of values
        """
        try:
            self.cur.executemany(command, valueset)
        except Exception as e:
            self.connect()  # Reload database
            raise


DB = DatabaseHandler()

if __name__ == "__main__":
    logger.critical("Please run the command via TODO")
    exit()
