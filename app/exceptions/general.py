from fastapi import status
from .base import HTTPBase


class JWTUnauthorizeException(
    HTTPBase,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
): pass


class InstanceDoesNotExistException(
    HTTPBase,
    status_code=status.HTTP_404_NOT_FOUND,
    detail="instance not found",
): pass


class AWSClientException(
    HTTPBase,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="upload image error due to network, service, permission etc...",
): pass


class AWSLimitExceededException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="API rate limit exceeded, backing off and retrying",
): pass


class AWSParamValidationException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="invalid or not found cloud argument",
): pass


class ConvertDatetimeFormatException(Exception):
    error_message: str = "datetime arugment type error or tzinfo not UTC"

    def __str__(self):
        return self.error_message


class InstanceFieldException(
    HTTPBase,
    detail="錯誤排序欄位",
    status_code=status.HTTP_400_BAD_REQUEST,
): pass
