from .base import *
import sentry_sdk

DOCS_URL = None
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