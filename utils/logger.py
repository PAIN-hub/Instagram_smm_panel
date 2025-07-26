import logging
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)

    # Main logger for general info
    logger = logging.getLogger("main_logger")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    success_handler = logging.FileHandler("logs/success.log")
    success_handler.setLevel(logging.INFO)
    success_handler.setFormatter(formatter)
    logger.addHandler(success_handler)

    error_handler = logging.FileHandler("logs/error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger

logger = setup_logger()