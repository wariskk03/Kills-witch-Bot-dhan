import logging
import os
from logging.handlers import RotatingFileHandler

def log_config(name):
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    
    error_log = os.path.join(log_path, "error.log")
    activity_log = os.path.join(log_path, "activity.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:

        # format for all handlers
        format = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        
        # activity log handler
        activity_handler = RotatingFileHandler(activity_log, maxBytes=5_000_000, backupCount=3)
        activity_handler.setLevel(logging.DEBUG)
        activity_handler.addFilter(lambda record: logging.DEBUG < record.levelno < logging.ERROR)
        activity_handler.setFormatter(format)
        logger.addHandler(activity_handler)

        # error log handler
        error_handler = RotatingFileHandler(error_log, maxBytes=5_000_000, backupCount=3)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(format)
        logger.addHandler(error_handler)

        # stream log handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        stream_handler.addFilter(lambda record: record.levelno < logging.ERROR)
        logger.addHandler(stream_handler)

    return logger
