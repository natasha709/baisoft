import os
import sys

# Ensure the backend directory is at the front of the path
# This MUST happen before pytest-django loads settings
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Also add parent directory (project root) to ensure proper package resolution
project_root = os.path.dirname(backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def pytest_configure(config):
    """
    Additional pytest configuration hook.
    """
    pass
