import sentry_sdk
from .base import *


CORS_ORIGINS: list = [
    "http://127.0.0.1:3000",
]
CORS_METHODS: list = [
    "GET",
    "POST",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
TRUSTS_HOSTS = [
    "*.neochang.com"
]

SENTRY_DSN: str = os.getenv("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,
)