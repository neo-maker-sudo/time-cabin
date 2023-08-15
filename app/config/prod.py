from .base import *
import sentry_sdk

CORS_ORIGINS: list = []
CORS_METHODS: list = [
    "GET",
    "POST",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
TRUSTS_HOSTS: list = []

SENTRY_DSN: str = os.getenv("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.5,
)