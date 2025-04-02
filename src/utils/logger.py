import json
import logging
from src.config import logging_config as LOGCONF

pretty_logger = LOGCONF.get_pretty_logger("pretty_logger")

# New function to append report text
def write_to_report(text: str, file_path: str = "/Users/riteshshah/github-adhirathee/NAI/NohaAI-Prototype-2/report.txt"):
    """Appends text to a report file without timestamps or log levels.

    Args:
        text (str): The content to append.
        file_path (str, optional): The file to write to. Defaults to 'report.txt'.
    """
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")  # Append text with a newline
    except Exception as e:
        log_error(f"Error writing to report file: {e}", exc_info=True)


def pretty_log(title: str, data, log_level=LOGCONF.INFO, compact=False):
    """
    Logs a structured dictionary or list in either compact or pretty JSON format.
    - Logs to both console and file.
    
    Args:
        title (str): A descriptive title for the log entry.
        data (dict | list | any): The structured data to log.
        log_level (int, optional): Logging level (default is INFO).
        compact (bool, optional): If True, logs as a single-line JSON. Otherwise, pretty-prints. Default is False.
    """
    try:
        # Convert data to JSON (compact or pretty)
        if isinstance(data, (dict, list)):
            pretty_data = json.dumps(data, indent=None if compact else 4, ensure_ascii=False)
        else:
            pretty_data = str(data)

        log_message = f"\n==== {title} ====\n{pretty_data}\n================="

        # Check if log level is enabled before printing
        # if pretty_logger.isEnabledFor(log_level):
        #     print(log_message)  # Print to console only if log level is allowed


        # Log to file using logging module
        pretty_logger.log(log_level, log_message)

    except Exception as e:
        log_error(f"Error while logging {title}: {e}", exc_info=True)


    # === NEW HELPER FUNCTIONS FOR SIMPLE LOGGING ===
def log_info(message: str):
    """Logs an info message."""
    pretty_logger.info(message)

def log_warning(message: str):
    """Logs a warning message."""
    pretty_logger.warning(message)

def log_error(message: str, exc_info=False):
    """
    Logs an error message.
    - If `exc_info=True`, it captures and logs the full stack trace.
    """
    if exc_info:
        pretty_logger.exception(message)  # Logs full stack trace
    else:
        pretty_logger.error(message)

def log_debug(message: str):
    """Logs a debug message."""
    pretty_logger.debug(message)

def log_critical(message: str):
    """Logs a critical error."""
    pretty_logger.critical(message)

# Function to log messages at custom levels
def debug1(self, message, *args, **kwargs):
    if self.isEnabledFor(LOGCONF.DEBUG1):
        self._log(LOGCONF.DEBUG1, message, args, **kwargs)

def debug2(self, message, *args, **kwargs):
    if self.isEnabledFor(LOGCONF.DEBUG2):
        self._log(LOGCONF.DEBUG2, message, args, **kwargs)

# Attach custom methods to logger
logging.Logger.debug1 = debug1
logging.Logger.debug2 = debug2

def log_debug1(message: str):
    """Logs a debug message at the DEBUG1 level."""
    pretty_logger.debug1(message)

def log_debug2(message: str):
    """Logs a debug message at the DEBUG2 level."""
    pretty_logger.debug2(message)