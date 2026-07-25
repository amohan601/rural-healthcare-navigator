import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

from src.backend.logging.formatter import JsonFormatter

logger = logging.getLogger("rural_health")

if LOG_LEVEL == "DEBUG":
    print('[logger] Setting level DEBUG')
    logger.setLevel(logging.DEBUG)
else:
    print('[logger] Setting level INFO')
    logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/app.log")

handler.setFormatter(JsonFormatter())

logger.addHandler(handler)