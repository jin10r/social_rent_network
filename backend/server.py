"""
ASGI entrypoint expected by supervisor as "server:app".
Select backend app based on environment:
- USE_POSTGRES=true -> use main (PostgreSQL + PostGIS)
- otherwise -> use main_simple (SQLite)
This lets us run locally with SQLite but in docker/k8s with Postgres.
"""
import os

USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() in {"1", "true", "yes"}

if USE_POSTGRES:
    from main import app  # noqa: F401
else:
    from main_simple import app  # noqa: F401