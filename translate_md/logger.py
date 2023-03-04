"""Simple logging facilities for the client. """

import logging
import logging.config

CONFIG = {
    "format": "%(asctime)s.%(msecs)03d | %(levelname)-7s | %(name)s - %(message)s",
    "datefmt": "%H:%M:%S",
}


def get_logger(name: str = None) -> logging.Logger:
    """Get the logger for the client.

    Its intended for internal use.

    Args:
        name (str, optional):
            Name of the logger. Defaults to None.

    Returns:
        logging.Logger: object ready to write content.
    """
    logging.config.dictConfig(CONFIG)
    logger = logging.getLogger(name)
    return logger
