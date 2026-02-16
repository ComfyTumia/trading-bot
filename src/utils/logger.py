from loguru import logger
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger.remove()
    logger.add("logs/app.log", rotation="5 MB", retention="14 days", level="INFO")
    logger.add(lambda msg: print(msg, end=""), level="INFO")
    return logger