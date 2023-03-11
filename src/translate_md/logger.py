"""Simple logging facilities for the client. """

import logging
import logging.config

CONFIG = {
    "version": 1,
    # "datefmt": "%H:%M:%S",
    "level": "INFO",
    "formatters": {
        "standard": {
            "format": "%(asctime)s.%(msecs)03d | %(levelname)-7s | %(name)s - %(message)s"
        },
    },
    # "handlers": {
    #     "default": {
    #         "level": "INFO",
    #         "formatter": "standard",
    #         "class": "logging.StreamHandler",
    #         "stream": "ext://sys.stdout",  # Default is stderr
    #     },
    # },
    "loggers": {
        "": {
            "level": "INFO",
        },
    },
}

CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {"format": "%(asctime)s.%(msecs)03d | %(levelname)-7s | %(name)s - %(message)s"},
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


def get_logger(name: str = None) -> logging.Logger:
    """Get the logger for the client.

    Its intended for internal use.

    Args:
        name (str, optional):
            Name of the logger. Defaults to None.

    Returns:
        logging.Logger: object ready to write content.
    """
    # logging.config.dictConfig(CONFIG)
    logger = logging.getLogger(name)
    return logger
