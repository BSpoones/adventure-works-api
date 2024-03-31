from mysql.connector import connect
from os.path import isfile
import json, logging, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mysql.connector.cursor import CursorBase
from mysql.connector import MySQLConnection

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DatabaseHandler:
    _instance = None
    _initialised = False

    """
    Creating a makeshift singleton object via an instance check
    
    Regardless of how many times DatabaseHandler is called, only
    one instance will be used. This allows for direct access
    anywhere in the program without tying it to a variable, making
    it more secure and minimizing the risk of accidental overwriting
    """

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.info("Creating a new instance of the Database Handler")
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    """
    Ensures that the DatabaseHandler is initialised
    only once, allowing for direct access anywhere
    """
    def __init__(self):
        if not self._initialised:
            logger.info("INITIALISING")
            self._initialised = True


if __name__ == "__main__":
    logger.info("AGFSDAG")
    x = DatabaseHandler()
    y = DatabaseHandler()
    z = DatabaseHandler()
