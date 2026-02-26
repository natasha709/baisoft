"""
WSGI Configuration for Product Marketplace
==========================================

WSGI (Web Server Gateway Interface) is the Python standard for web applications.
This module provides the WSGI callable that production web servers use to 
communicate with the Django application.

What is WSGI?
- Standard interface between web servers and Python web applications
- Allows Django to run on various web servers (Apache, Nginx + Gunicorn, etc.)
- Handles the request/response cycle between server and application

Production Deployment:
- Use with Gunicorn: gunicorn config.wsgi:application
- Use with uWSGI: uwsgi --module=config.wsgi:application
- Configure with reverse proxy (Nginx) for static files and load balancing

Environment Setup:
- Automatically sets DJANGO_SETTINGS_MODULE to production settings
- Ensure all environment variables are properly configured
- Verify database connections and static file serving

Security Considerations:
- Set DEBUG=False in production settings
- Configure ALLOWED_HOSTS with your domain names
- Use HTTPS in production with proper SSL certificates
- Set up proper logging and error monitoring
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the Django settings module for the WSGI application
# This tells Django which settings file to use when the application starts
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the WSGI application callable
# This is what production web servers will use to communicate with Django
application = get_wsgi_application()
