import logging
from src.config import logging_config as LOGCONF

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger instance.

    Args:
        name: Name of the logger (usually `__name__`).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if LOGCONF.ENABLE_LOGGING:
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
        file_handler = logging.FileHandler('noha_ai_prototype.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        logger.disabled = True

    return logger

def get_logger_prev(name: str) -> logging.Logger:
    """Configures and returns a logger instance.

    Args:
        name: Name of the logger (usually `__name__`).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    file_handler = logging.FileHandler('noha_ai_prototype.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
