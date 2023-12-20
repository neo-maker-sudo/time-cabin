from .base import HTTPBase
from fastapi import status


class RequestsTimeoutException(
    HTTPBase,
    status_code=status.HTTP_408_REQUEST_TIMEOUT,
    detail="連線逾時"
): pass


class RequestsHttpErrorException(
    HTTPBase,
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="網路連線錯誤"
): pass


class RequestsInvalidException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無法取得資源"
): pass
