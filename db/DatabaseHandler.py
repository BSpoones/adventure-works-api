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
    def __init__(self):
        pass



database_handler = DatabaseHandler()

if __name__ == "__main__":
    logger.info("AGFSDAG")
