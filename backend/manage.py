#!/usr/bin/env python
"""
Django Management Script - Entry Point for Administrative Tasks
===============================================================

This is Django's standard command-line utility for administrative tasks.
It serves as the main entry point for running Django management commands.

Common Commands:
- python manage.py runserver          # Start development server
- python manage.py migrate            # Apply database migrations
- python manage.py createsuperuser    # Create admin user
- python manage.py collectstatic      # Collect static files for production
- python manage.py test               # Run test suite
- python manage.py shell              # Open Django shell
- python manage.py makemigrations     # Create new database migrations

Environment Setup:
- Automatically sets DJANGO_SETTINGS_MODULE to 'config.settings'
- Requires Django to be installed and available in PYTHONPATH
- Should be run from within activated virtual environment

Error Handling:
- Provides clear error message if Django is not installed
- Suggests checking virtual environment activation
- Maintains original exception chain for debugging
"""
import os
import sys


def main():
    """
    Run administrative tasks.
    
    This function:
    1. Sets the default Django settings module
    2. Imports Django's command-line execution utility
    3. Executes the command with provided arguments
    4. Handles ImportError if Django is not properly installed
    
    Raises:
        ImportError: If Django is not installed or not in PYTHONPATH
    """
    # Set default settings module for Django configuration
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        # Import Django's command-line utility
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Provide helpful error message if Django is not available
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Execute the command with command-line arguments
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
