"""Simple logging facilities for the client. """

import logging
import logging.config

FORMAT = "%(asctime)s.%(msecs)03d | %(levelname)-7s | %(name)s - %(message)s"

CONFIG = {
    "version": 1,
    "level": "INFO",
    "formatters": {
        "standard": {"format": FORMAT},
    },
    "loggers": {
        "": {
            "level": "INFO",
        },
    },
}

CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {"format": FORMAT},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(CONFIG)


def get_logger(name: str = "client") -> logging.Logger:
    """Get the logger for the client.

    Its intended for internal use.

    Args:
        name (str, optional):
            Name of the logger. Defaults to None.

    Returns:
        logging.Logger: object ready to write content.
    """
    logger = logging.getLogger(name)
    return logger
