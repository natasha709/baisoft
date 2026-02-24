"""
Logging Configuration for BAISoft Product Marketplace

This module configures structured logging for the Django application.
It supports both console output (development) and file output (production).
"""

import logging
import logging.config
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_directory():
    """Get or create the logs directory."""
    log_dir = Path(__file__).resolve().parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    return log_dir


def configure_logging():
    """
    Configure application logging with appropriate formatters and handlers.
    
    Log Levels:
    - DEBUG: Detailed information for diagnosing problems
    - INFO: Confirmation that things are working as expected
    - WARNING: Something unexpected happened, but the app still works
    - ERROR: A serious problem occurred, the app failed to perform
    - CRITICAL: A very serious error that may cause the app to stop
    
    Log Files:
    - django.log: General Django logs
    - error.log: Error and critical logs only
    - audit.log: Audit logs for security-sensitive operations
    """
    
    # Determine if we're in production
    is_production = os.environ.get('DEBUG', '').lower() != 'true'
    
    log_dir = get_log_directory()
    
    # Base configuration
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    detailed_format = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    )
    
    # JSON format for production (structured logging)
    json_format = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s", '
        '"file": "%(filename)s", "line": %(lineno)d}'
    )
    
    handlers = {
        # Console handler for development
        'console': {
            'class': 'logging.StreamHandler',
            'level': logging.DEBUG if not is_production else logging.INFO,
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
    }
    
    # Add file handlers for production
    if is_production:
        handlers.update({
            # General Django logs (rotating, max 10MB, keep 5 backups)
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'json',
                'filename': str(log_dir / 'django.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8',
            },
            # Error logs only
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.ERROR,
                'formatter': 'json',
                'filename': str(log_dir / 'error.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8',
            },
            # Audit logs for security-sensitive operations
            'audit_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'detailed',
                'filename': str(log_dir / 'audit.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 10,
                'encoding': 'utf-8',
            },
        })
    else:
        # Development: also write to a debug file
        handlers.update({
            'debug_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.DEBUG,
                'formatter': 'detailed',
                'filename': str(log_dir / 'debug.log'),
                'maxBytes': 5 * 1024 * 1024,  # 5MB
                'backupCount': 3,
                'encoding': 'utf-8',
            },
        })
    
    formatters = {
        'simple': {
            'format': log_format,
        },
        'detailed': {
            'format': detailed_format,
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': json_format,
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    }
    
    # Root logger configuration
    root_level = logging.DEBUG if not is_production else logging.INFO
    
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': handlers,
        'loggers': {
            # Django loggers
            'django': {
                'handlers': ['console'] + (['file', 'error_file'] if is_production else ['debug_file']),
                'level': root_level,
                'propagate': False,
            },
            'django.request': {
                'handlers': ['console'] + (['error_file'] if is_production else ['debug_file']),
                'level': logging.WARNING,
                'propagate': False,
            },
            'django.security': {
                'handlers': ['console'] + (['error_file', 'audit_file'] if is_production else ['debug_file']),
                'level': logging.WARNING,
                'propagate': False,
            },
            # Third-party loggers
            'django.db.backends': {
                'handlers': ['console'] if not is_production else ['file'],
                'level': logging.WARNING,  # Don't log SQL queries in production
                'propagate': False,
            },
            'urllib3': {
                'handlers': ['console'],
                'level': logging.WARNING,
                'propagate': False,
            },
            # Application loggers
            'products': {
                'handlers': ['console'] + (['audit_file'] if is_production else ['debug_file']),
                'level': logging.INFO,
                'propagate': False,
            },
            'businesses': {
                'handlers': ['console'] + (['audit_file'] if is_production else ['debug_file']),
                'level': logging.INFO,
                'propagate': False,
            },
            'chatbot': {
                'handlers': ['console'] + (['file'] if is_production else ['debug_file']),
                'level': logging.INFO,
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console'] + (['file'] if is_production else ['debug_file']),
            'level': root_level,
        },
    })


# Audit logger for security-sensitive operations
def get_audit_logger(name: str = 'audit') -> logging.Logger:
    """Get a dedicated audit logger for security-sensitive operations."""
    audit_logger = logging.getLogger(f'audit.{name}')
    audit_logger.setLevel(logging.INFO)
    
    # Ensure audit logs go to the audit file
    if not any(isinstance(h, logging.FileHandler) and 'audit' in getattr(h, 'baseFilename', '') 
               for h in audit_logger.handlers):
        log_dir = get_log_directory()
        handler = RotatingFileHandler(
            log_dir / 'audit.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding='utf-8'
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        audit_logger.addHandler(handler)
    
    return audit_logger


# Convenience function to log API requests
def log_api_request(logger: logging.Logger, request, response_status: int, duration_ms: float):
    """Log API request details in a structured format."""
    logger.info(
        f"API Request: {request.method} {request.path} - "
        f"Status: {response_status} - Duration: {duration_ms:.2f}ms"
    )
