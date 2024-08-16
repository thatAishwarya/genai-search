import logging
from config import SETTINGS

def setup_logging():
    logging.basicConfig(
        level=SETTINGS["LOGGING_LEVEL"],
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger
