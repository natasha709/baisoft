import os
import sys

def pytest_configure(config):
    """
    Configure Python path before any tests are loaded.
    This ensures Django settings can be imported correctly.
    """
    # Get the backend directory (where this file is located)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure the backend directory is in the path
    # This allows imports like 'from config.logging' to work
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
