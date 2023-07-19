from fastapi import HTTPException, status


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


class InstanceDoesNotExistException(
    HTTPBase,
    status_code=status.HTTP_404_NOT_FOUND,
    detail="instance not found",
):
    ...


class AWSClientException(
    HTTPBase,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="upload image error due to network, service, permission etc...",
):
    ...


class AWSLimitExceededException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="API rate limit exceeded, backing off and retrying",
):
    ...


class AWSParamValidationException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="invalid or not found cloud argument",
):
    ...


class VideoFileExtensionException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="invalid file extension"
): pass


class ConvertDatetimeFormatException(Exception):
    error_message: str = "datetime arugment type error or tzinfo not UTC"

    def __str__(self):
        return self.error_message
