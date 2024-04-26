import logging
from dataclasses import fields

from util.Singleton import singleton
from .DataType import DataType

from MySQLdb.cursors import Cursor, DictCursor
from MySQLdb import Connection
from MySQLdb import Connect

from db.model.base.Table import Table
from util.Repeat import repeat

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

"""
Since environment variables aren't allowed for this assignment,
I have stored these in constants. In a real world situation, i would
add these to a .env file
"""
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "aaaaaa"
DB_DATABASE = "adventureworks2019"


@singleton
class DatabaseHandler:
    """
    Database Handler

    A custom database handler to handle all aspects of a database required for
    this assignment

    This class is a singleton, to prevent the creation of multiple cursors
    """

    def __init__(self) -> None:
        self.cur = None
        self.cxn = None
        self.connect()

    @staticmethod
    def with_commit(func) -> None:
        """
        with_commit decorator

        Auto-commits any function run with this decorator

        :param func:
        :return:
        """

        def inner(self, *args, **kwargs):
            if kwargs.get("with_commit", True):
                self.commit()
            return func(self, *args, **kwargs)

        return inner

    @property
    def cursor(self) -> DictCursor:
        """
        Property to retrieve the cursor when used outside the
        database handler
        :return: DictCursor
        """
        return self.cur

    def connect(self) -> None:
        """
        Connects | Reconnects to the database
        """
        if self.cur is None or self.cxn is None:
            logger.warning("Connecting to the database")
            self.cxn: Connection = Connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            )
            self.cur: Cursor = self.cxn.cursor(cursorclass=DictCursor)

    @with_commit
    def close(self, log: bool = True) -> None:
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
            if log:
                logger.info("Successfully closed")

        except Exception:
            logger.critical("Failed to close connection")

    def commit(self) -> None:
        """
        Commits to the db
        """
        logger.debug("Committing")
        self.cxn.commit()

    def _get_data(self, data_type: DataType, command: str, values: tuple) -> None | list | int:
        """
        Gets data from the db dependent on the command and values and
        returns an output based on the data type

        Args:
            data_type (DataType): Data type
            command (str): SQL command
            values (tuple): Values for command substitution

        Returns:
            str: Database output
        """
        self.execute(command, values)
        return data_type.get_data(self.cur)

    def record(self, command: str, *values) -> dict[str, any]:
        """
        Returns a single db row

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            tuple: Single row command output
        """
        return self._get_data(DataType.RECORD, command, values)

    def records(self, command: str, *values) -> list[any]:
        """
        Returns all db rows

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            list(tuple): All command output rows
        """
        return self._get_data(DataType.RECORDS, command, values)

    def column(self, command: str, *values) -> int:
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

    def count(self, command: str, *values) -> int:
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

    def last_row_id(self) -> None:
        """
        Retrieves the row ID of the most
        recent cursor command

        Returns:
            int: Row ID
        """
        return self.cur.lastrowid

    def is_in_db(self, table: Table, col: str, value: str) -> dict[str, any]:
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
        table_name = table.table_name()
        # NOTE: SQL injection is not possible as the f string values
        # are constants set in code. No user inputs are inserted
        command = f"SELECT * FROM {table_name} WHERE {col} = %s"
        return self.record(command, value)

    @with_commit
    def insert(self, table: Table, with_commit: bool = True) -> tuple | None:
        """
        Inserts data into the database

        Args:
            table (Table): Db table
            with_commit (bool, optional): Should a commit occur after this insertion.
            Defaults to True.
        """
        table_name = table.table_name()
        cols = [field[0] for field in table.model_fields.items()]
        data = [getattr(table, field[0]) for field in table.model_fields.items()]
        cols_str = ",".join(cols)

        # Workaround to add nulls to the database
        data_str = ",".join(["?" if x is not None else "NULL" for x in data])

        # NOTE: SQL injection is not possible as the f string values
        # are constants set in code. No user inputs are inserted
        self.execute(
            f"INSERT INTO {table_name} ({cols_str}) VALUES ({data_str})",
            *data
        )
        return table.get_from_id(self.cur.lastrowid)

    @with_commit
    def delete(self, table: Table, with_commit: bool = True) -> bool:
        """
        Deletes data from the database

        Args:
            table (Table): Db table
            with_commit (bool, optional): Should a commit occur after this insertion.
            Defaults to True.
        """
        table_name = table.table_name()
        primary_key_name = table.primary_key_name()
        primary_key_value = table.get_primary_key()

        try:
            # NOTE: SQL injection is not possible as the f string values
            # are constants set in code. No user inputs are inserted
            self.execute(
                f"DELETE FROM {table_name} WHERE {primary_key_name} = %s", (primary_key_value,)
            )
            return True
        except Exception as e:
            logger.error(repr(e))
            return False
        finally:
            # Ensures that a commit takes place regardless of the error
            self.commit()

    @with_commit
    def update(self, table: Table, primary_key_value: int, with_commit: bool = True) -> tuple:
        """
        Inserts data into the database

        Args:
            table (Table): Db table
            :param table:
            :param primary_key_value:
            :param with_commit: (bool, optional): Should a commit occur after this insertion.
            Defaults to True.
        """
        table_name = table.table_name()
        primary_key_name = table.primary_key_name()

        cols = [field[0] for field in table.model_fields.items() if getattr(table, field[0]) is not None] or []
        data = [getattr(table, field[0]) for field in table.model_fields.items() if
                getattr(table, field[0]) is not None] or []
        data.append(primary_key_value)
        clauses = [f"{col} = %s" for col in cols]
        clauses_str = ", ".join(clauses)

        # NOTE: SQL injection is not possible as the f string values
        # are constants set in code. No user inputs are inserted
        self.execute(
            f"UPDATE {table_name} SET {clauses_str} WHERE {primary_key_name} = %s",
            *data,
        )

        return table.create_update(
            **self.record(
                f"SELECT * FROM {table_name} WHERE {primary_key_name} = %s",
                primary_key_value
            )
        )

    def get_next_id(self, table: Table) -> int:
        primary_key_name = table.primary_key_name()
        table_name = table.table_name()
        print(primary_key_name, table_name)
        return self.count(f"SELECT MAX({primary_key_name}) FROM {table_name}") + 1

    @repeat(retries=3)
    @with_commit
    def execute(self, command: str, *values) -> None:
        """
        Executes a database command

        Args:
            command (str): SQL command
        Raises:
            LookupError: If the max retries limit has exceeded
        """
        # Removes nested tuples
        if len(values) == 1:
            values = values[0]
        values = values if values != ((),) else None

        try:
            return self.cur.execute(command, values)
        except Exception as e:
            # A typical error in MySql python is the connection
            # expiring; this should fix it
            self.connect()
            raise e


DB = DatabaseHandler()

if __name__ == "__main__":
    logger.critical("Please run the command via the command line")
    exit()
