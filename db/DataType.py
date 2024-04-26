from enum import Enum

import logging
from MySQLdb.cursors import DictCursor

logger = logging.getLogger(__name__)


class DataType(Enum):
    """
    DataType Enum

    Represents all possible actions to retrieve data from the
    AdventureWorks2019 database
    """

    RECORD = 0,
    RECORDS = 1,
    COLUMN = 2,
    COUNT = 3

    def get_data(self, cursor: DictCursor) -> None | list | int:
        match self:
            case self.RECORD:
                return cursor.fetchone()
            case self.RECORDS:
                return cursor.fetchall()
            case self.COLUMN:
                response_dict = cursor.fetchone()
                items = list(response_dict.items())
                if not items:
                    return None
                else:
                    return items[0]

            case self.COUNT:
                return int((list(cursor.fetchone().values())[0]))
            case _:
                raise KeyError("Invalid data type")
