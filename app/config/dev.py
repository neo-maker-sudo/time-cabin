from .base import *

DATABASE_URL: str = "postgres://postgres:postgres@127.0.0.1:5432/time_cabin"
REDIS_URL: str = "redis://localhost:6379"
DOCS_URL: str = "/docs"
CORS_ORIGINS: list = [
    "*"
]
CORS_METHODS: list = [
    "GET",
    "POST",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
TRUSTS_HOSTS = None
