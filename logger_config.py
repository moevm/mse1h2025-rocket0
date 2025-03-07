import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import json

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "mse1h2025-rocket0.log")

logger = logging.getLogger("mse1h2025-rocket0")
logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
json_formatter = json.JsonFormatter(
"%(asctime)s %(name)s %(levelname)s %(message)s",
    rename_fields={"asctime": "timestamp", "name": "name", "levelname": "level", "message": "msg"},
)

# Вывод в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(json_formatter)

# Вывод в файл
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=5, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(json_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)