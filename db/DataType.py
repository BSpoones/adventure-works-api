from enum import Enum

import logging
from MySQLdb.cursors import Cursor

logger = logging.getLogger(__name__)


class DataType(Enum):
    RECORD = 0,
    RECORDS = 1,
    COLUMN = 2,
    COUNT = 3

    def get_data(self, cur: Cursor):
        match self:
            case self.RECORD:
                return cur.fetchone()
            case self.RECORDS:
                return cur.fetchall()
            case self.COLUMN:
                return [item[0] for item in cur.fetchall()]
            case self.COUNT:
                return int(cur.fetchone()[0])
            case _:
                raise KeyError("Invalid data type")
