from logging import getLogger, DEBUG, INFO, WARNING, StreamHandler, Formatter
from logging.handlers import QueueHandler, RotatingFileHandler
from multiprocessing import Queue
import sys


def main_logger_configure() -> None:
    logger = getLogger()
    logger.setLevel(DEBUG)
    log_format = Formatter("%(asctime)s - %(processName)s - %(levelname)s - %(message)s")
    shandler = StreamHandler(sys.stdout)
    debug_fhandler = RotatingFileHandler("debug.log", "a+", (5*1024*512), 1)
    error_fhandler = RotatingFileHandler("error.log", "a+", (5*1024*512), 1)
    shandler.setFormatter(log_format)
    debug_fhandler.setFormatter(log_format)
    error_fhandler.setFormatter(log_format)
    shandler.setLevel(INFO)
    debug_fhandler.setLevel(DEBUG)
    error_fhandler.setLevel(WARNING)
    logger.addHandler(shandler)
    logger.addHandler(debug_fhandler)
    logger.addHandler(error_fhandler)


def queue_logger_configure(queue: Queue) -> None:
    handler = QueueHandler(queue)
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
