import logging
from logging.handlers import RotatingFileHandler

def log_config(name, file_path, file_level=logging.INFO, console_level:list=[logging.DEBUG, logging.INFO]):
    
    # create logger and pass all level to handlers
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        
        # set file handler
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=5_000_000,
            backupCount=3
        )
        format = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        file_handler.setFormatter(format)
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)

        # set stream handler
        console_handler = logging.StreamHandler()
        format_con = logging.Formatter("%(message)s")
        console_handler.addFilter(lambda record: record.levelno in console_level)
        console_handler.setFormatter(format_con)
        logger.addHandler(console_handler)

    return logger
