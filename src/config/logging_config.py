# Logging configurations

### Example 

import logging, os
from src.config import env_settings as ENV

# Define custom log levels
DEBUG1 = 9
DEBUG2 = 8
# Register these levels with logging module
logging.addLevelName(DEBUG1, "DEBUG1")
logging.addLevelName(DEBUG2, "DEBUG2")

# Define log level aliases to avoid importing `logging` everywhere
LOG_LEVELS = {
    "DEBUG2": DEBUG2,
    "DEBUG1": DEBUG1,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Allow accessing levels dynamically
DEBUG2 = LOG_LEVELS["DEBUG2"]
DEBUG1 = LOG_LEVELS["DEBUG1"]
DEBUG = LOG_LEVELS["DEBUG"]
INFO = LOG_LEVELS["INFO"]
WARNING = LOG_LEVELS["WARNING"]
ERROR = LOG_LEVELS["ERROR"]
CRITICAL = LOG_LEVELS["CRITICAL"]


###
# Toggle ENABLE_LOGGING to enable/disable logging. 
# note: This only disables logging output; logging calls will still be executed. To eliminate latency from log statements, remove them from the production code.
ENABLE_LOGGING = True  

def get_pretty_logger(name: str) -> logging.Logger:
    """Configures and returns a logger instance.

    Args:
        name: Name of the logger (usually `__name__`).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Define logging format, file name, and minimum logging level specific to this logger

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    FILENAME = "noha_ai_prototype.log"
    FILEPATH = os.path.join(ENV.BASE_DIR, FILENAME)
    LEVEL = INFO    # Set the minimum logging level here
    print("FILEPATH: ", FILEPATH)
    name_logger = logging.getLogger(name)

    if ENABLE_LOGGING:
        print("ENABLE_LOGGING: ", ENABLE_LOGGING)
        if not name_logger.hasHandlers():
            print("name_logger.hasHandlers(): ", name_logger.hasHandlers())
            formatter = logging.Formatter(LOG_FORMAT)  
            file_handler = logging.FileHandler(FILENAME)
            file_handler.setFormatter(formatter)
            name_logger.addHandler(file_handler)
            name_logger.setLevel(LEVEL)
    else:
        name_logger.disabled = True

    return name_logger
