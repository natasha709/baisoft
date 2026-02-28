"""
Logging configuration for BAISoft Product Marketplace

This module provides custom logging configuration for the application.
"""

import logging
import logging.config
import os
from pathlib import Path

def configure_logging():
    """
    Configure logging for the application.

    This sets up structured logging with different levels for different
    components, making it easier to debug and monitor the application.
    """

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    loggers = {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'rest_framework': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    }

    for logger_name, logger_config in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_config['level'])
        for handler in logger_config.get('handlers', ['console']):
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
                logger.addHandler(handler)

    return logging.getLogger('django')
