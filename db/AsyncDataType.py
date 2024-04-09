from enum import Enum

import MySQLdb, logging
logger = logging.getLogger(__name__)


class AsyncDataType(Enum):
    RECORD = 0,
    RECORDS = 1,
    COLUMN = 2,
    COUNT = 3

    async def get_data(self, cur):
        match self:
            case self.RECORD:
                return await cur.fetchone()
            case self.RECORDS:
                return await cur.fetchall()
            case self.COLUMN:
                return [item[0] for item in await cur.fetchall()]
            case self.COUNT:
                return int(await cur.fetchone()[0])
            case _:
                raise KeyError("Invalid data type")
