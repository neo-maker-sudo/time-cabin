from fastapi import HTTPException


class HTTPBase(Exception):
    status_code = None
    detail = None
    headers = None

    @classmethod
    def raise_http_exception(cls):
        raise HTTPException(
            status_code=cls.status_code,
            detail=cls.detail,
            headers=cls.headers,
        )

    def __init_subclass__(cls, **kwargs) -> None:
        for key, value in kwargs.items():
            type.__setattr__(cls, key, value)
