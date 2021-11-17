import datetime
import logging
import sys

root_logger = logging.getLogger("rov-vision")


def init_logger():
    root_logger.setLevel(logging.DEBUG)

    # Send all log messages to a file
    filename = datetime.datetime.now().strftime("logs/%Y-%m-%d_%H%M%S.log")
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # Send INFO and WARNING log messages to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    # Messages of severity above warning go to stderr instead
    stdout_handler.addFilter(lambda record: record.levelno <= logging.WARNING)
    root_logger.addHandler(stdout_handler)

    # Send ERROR and CRITICAL messages to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    root_logger.addHandler(stderr_handler)


init_logger()
