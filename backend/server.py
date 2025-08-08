"""
ASGI entrypoint expected by supervisor as "server:app".
This file simply re-exports the FastAPI app from main_simple.py (SQLite-based minimal backend).
All routes are already prefixed with /api where required.
"""

from main_simple import app  # noqa: F401