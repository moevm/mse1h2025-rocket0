import logging
import os
import tg_logger
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import json

LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name: str, level: int = logging.INFO, to_console: bool = False, to_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = json.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "name": "name", "levelname": "level", "message": "msg"},
    )

    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if to_file and len(to_file) > 0:
        file_handler = RotatingFileHandler(os.path.join(LOG_DIR, to_file), maxBytes=10000000, backupCount=5, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


telegram_logger = setup_logger("telegram", logging.INFO)
general_logger = setup_logger("general", logging.INFO, to_console=True)
requests_logger = setup_logger("requests", logging.INFO, to_file="requests.log", to_console=True)
debug_logger = setup_logger("debug", logging.DEBUG, to_console=True)


def add_telegram_handler(token: str, allowed_user_ids: list[int]) -> None:
    tg_logger.setup(telegram_logger, token=token, users=allowed_user_ids,
                    tg_format="<b>(%(levelname)s)</b> %(asctime)s: <code>%(message)s</code>")
