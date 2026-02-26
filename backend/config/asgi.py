"""
ASGI Configuration for Product Marketplace
==========================================

ASGI (Asynchronous Server Gateway Interface) is the spiritual successor to WSGI.
This module provides the ASGI callable for running Django with async capabilities.

What is ASGI?
- Supports both synchronous and asynchronous Python applications
- Enables WebSockets, HTTP/2, and other async protocols
- Backward compatible with WSGI applications
- Required for Django Channels (WebSockets, background tasks)

Current Usage:
- Basic HTTP requests (same as WSGI)
- Ready for future async features like WebSockets
- Can be used with async-capable servers (Daphne, Uvicorn)

Future Enhancements:
- Real-time notifications for product approvals
- Live chat functionality in the chatbot
- Real-time dashboard updates
- WebSocket connections for instant updates

Production Deployment:
- Use with Daphne: daphne config.asgi:application
- Use with Uvicorn: uvicorn config.asgi:application
- Configure with Redis for channel layers (if using Django Channels)

Performance Benefits:
- Better handling of concurrent connections
- Improved scalability for I/O-bound operations
- Support for long-lived connections (WebSockets)
"""

import os
from django.core.asgi import get_asgi_application

# Set the Django settings module for the ASGI application
# This tells Django which settings file to use when the application starts
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the ASGI application callable
# This handles both HTTP and potentially WebSocket connections
application = get_asgi_application()
