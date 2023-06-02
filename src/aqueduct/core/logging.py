"""
The `logging` module provides a logger implementation for the Aqueduct system.

Classes:
- AqLogger: A logger that writes log messages to a file at a configurable path.
"""
import logging
import os
from datetime import datetime
from typing import Union


class IsoTimeFormatter(logging.Formatter):
    """
    Custom log formatter that outputs the time in ISO format.
    """

    def formatTime(self, record, datefmt=None):
        """
        Formats the log record's creation time as an ISO-formatted string.

        Args:
                record (logging.LogRecord): The log record to format.
                datefmt (str, optional): The format string for the date/time. Defaults to None.

        Returns:
                str: The formatted date/time string.
        """
        return datetime.fromtimestamp(record.created).isoformat()


class AqLogger:
    """A class that wraps the Python logging module to create a logger that writes to a file.

    If the 'AQ_LOG_PATH' environment variable is not set,
    the path will be set to the current working directory.

    Attributes:
            logger (logging.Logger): The logger instance.
            log_path (str): The path to the log file.
    """

    _log_file_path: str
    _log_file_name: str
    _initialized: bool

    def __init__(self, log_file_name: Union[str, None], log_path: Union[str, None]):
        """
        Initializes an instance of the AqLogger.

        Args:
                log_file_name (Union[str, None]): The name of the log file. If None,
                it will be generated based on the current timestamp.
                log_path (Union[str, None]): The path to the log file. If None, it will
                default to the 'AQ_LOG_PATH' environment variable or the current working directory.
        """
        self._logger = logging.getLogger("AqLogger")
        self._logger.setLevel(logging.DEBUG)

        if log_path is None:
            log_path = os.environ.get("AQ_LOG_PATH")

        if log_path is None:
            log_path = os.getcwd()

        # Create file handler which logs messages to a file
        if log_file_name is None:
            log_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")

        self._log_file_path = log_path
        self._log_file_name = log_file_name
        self._initialized = False

    def set_log_file_name(self, log_file_name: str):
        """Set the log file name."""
        self._log_file_name = log_file_name

    def _init_logger(self):
        """Initialize the logger if not already initialized."""
        if not self._initialized:
            log_path = os.path.join(self._log_file_path, self._log_file_name)
            file_handler = logging.FileHandler(log_path)

            # Create formatter and add it to the file handler
            formatter = IsoTimeFormatter("%(asctime)s %(levelname)s %(message)s")
            file_handler.setFormatter(formatter)

            # Add the file handler to the logger
            self._logger.addHandler(file_handler)

            self._initialized = True

    def log(self, message: str):
        """Logs a message to the configured log file.

        Args:
                message (str): The message to log.
        """
        self._init_logger()
        self._logger.info(message)

    def debug(self, message):
        """
        Log a debug message.

        :param message: The message to log.
        :type message: str
        """
        self._init_logger()
        self._logger.debug(message)

    def info(self, message):
        """
        Log an info message.

        :param message: The message to log.
        :type message: str
        """
        self._init_logger()
        self._logger.info(message)

    def warning(self, message):
        """
        Log a warning message.

        :param message: The message to log.
        :type message: str
        """
        self._init_logger()
        self._logger.warning(message)

    def error(self, message):
        """
        Log an error message.

        :param message: The message to log.
        :type message: str
        """
        self._init_logger()
        self._logger.error(message)

    def critical(self, message):
        """
        Log a critical message.

        :param message: The message to log.
        :type message: str
        """
        self._init_logger()
        self._logger.critical(message)
