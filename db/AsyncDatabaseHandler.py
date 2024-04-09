import logging
import os
from functools import wraps

from AsyncDataType import AsyncDataType

from util.AsyncRepeat import async_repeat

from aiomysql import connect

logger = logging.getLogger("Async Database Handler")
logging.basicConfig(level=logging.DEBUG)


class AsyncDatabaseHandler:
    @classmethod
    async def create(cls):
        if any(x is None for x in (
                cls._get_host(),
                cls._get_user(),
                cls._get_db_password(),
                cls._get_database(),
        )):
            raise KeyError("Could not find database credentials in dotenv file!")

        instance = cls()
        await instance.connect()
        return instance

    @staticmethod
    def _get_host():
        return os.getenv("DB_HOST")

    @staticmethod
    def _get_user():
        return os.getenv("DB_USER")

    @staticmethod
    def _get_db_password():
        return os.getenv("DB_PASSWORD")

    @staticmethod
    def _get_database():
        return os.getenv("DB_DATABASE")

    @staticmethod
    async def with_commit(func):
        @wraps(func)
        async def inner(self, *args, **kwargs):
            if kwargs.get("with_commit", True):
                await self.commit()
            return await func(self, *args, **kwargs)

        return inner

    async def connect(self):
        """
        Connects | Reconnects to the database
        """
        if not hasattr(self, "cxn") or not hasattr(self, "cur"):
            self.cxn = connect(
                host=self._get_host(),
                user=self._get_user(),
                password=self._get_db_password(),
                db=self._get_database()
            )
            self.cur = self.cxn.cursor()
        else:
            logger.warning("Reconnecting")
            await self.close(log=False)

            await self.connect()
            logger.info("Successfully reconnected")

    @with_commit
    async def close(self, log: bool = True):
        """
        Closes the database connection

        Args:
            log (bool, optional): Log events to logger. Defaults to True.
        """
        try:
            if log:
                logger.warning("Closing connection")
            await self.cur.close()
            await self.cxn.close()

            delattr(self, "cur")
            delattr(self, "cxn")
            if log:
                logger.info("Successfully closed")

        except Exception:
            logger.critical("Failed to close connection")

    async def commit(self):
        """
        Commits to the db
        """
        logger.debug("Committing")
        await self.cxn.commit()

    async def _get_data(self, data_type: AsyncDataType, command, values):
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
        await self.execute(command, values)
        return await data_type.get_data(self.cur)

    async def record(self, command, *values):
        """
        Returns a single db row

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            tuple: Single row command output
        """
        return await self._get_data(AsyncDataType.RECORD, command, values)

    async def records(self, command, *values):
        """
        Returns all db rows

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            list(tuple): All command output rows
        """
        return await self._get_data(AsyncDataType.RECORDS, command, values)

    async def column(self, command, *values):
        """
        Returns a column of data.
        NOTE: A column must be specified

        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            tuple: Single column command output
        """
        return await self._get_data(AsyncDataType.COLUMN, command, values)

    async def count(self, command, *values):
        """
        Returns the first value in the first row of data
        Used to get the COUNT value


        Args:
            command (str): SQL command
            values (tuple): Command values

        Returns:
            int: Count output
        """
        return await self._get_data(AsyncDataType.COUNT, command, values)

    async def last_row_id(self):
        """
        Retrieves the row ID of the most
        recent cursor command

        Returns:
            int: Row ID
        """
        return await self.cur.lastrowid

    async def is_in_db(self, value, col, table: str) -> tuple:
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
        return await self.record(command, value)

    @with_commit
    async def insert(
            self,
            table: str,
            cols: list[str] | set[str],
            data: tuple,
            with_commit: bool = True):
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
        await self.execute(
            f"INSERT INTO {table_name} ({cols_str}) VALUES ({data_str})",
            *data
        )

    @async_repeat(retries=3)
    async def execute(self, command, *values):
        """
        Executes a database command

        Args:
            command (str): SQL command
            retries_left (int, optional): Amount of times the execute can run before it gives up. Defaults to MAX_RETRIES.

        Raises:
            LookupError: If the max retries limit has exceeded
        """
        # Removes nested tuples
        # TODO -> Rewrite this 2 year old dogshit code lol
        if len(values) == 1:
            values = values[0]

        values = values if values != ((),) else None
        try:
            return await self.cur.execute(command, values)
        except Exception as e:
            await self.connect()
            raise e

    @async_repeat(retries=3)
    async def multiexec(self, command, valueset):
        """
        Executes a database command multiple times using a valueset

        Args:
            command (str): SQL command
            valueset (set(tuple)): Set of values
        """
        try:
            await self.cur.executemany(command, valueset)
        except Exception as e:
            await self.connect()  # Reload database
            raise


A_DB = AsyncDatabaseHandler()

if __name__ == "__main__":
    logger.critical("Please run the command via TODO")
    exit()
