import os

POSTGRES_USER = os.environ.get("POSTGRES_USER") or "postgres"
POSTGRES_HOST = os.environ.get("POSTGRES_HOST") or "localhost"
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") or "postgres"
POSTGRES_DB = os.environ.get("POSTGRES_DB") or "auth"
POSTGRES_PORT = os.environ.get("POSTGRES_PORT") or 5432
JWT_SECRET = os.environ.get("JWT_SECRET") or "secret"
SERVICE_NAME = os.environ.get("SERVICE_NAME") or "auth"
