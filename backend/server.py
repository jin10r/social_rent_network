"""
ASGI entrypoint expected by supervisor as "server:app".
Switch to full Postgres-powered app for matching & likes testing.
"""
from main import app  # noqa: F401