from fastapi import status
from .base import HTTPBase


class JWTUnauthorizeException(
    HTTPBase,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="無效或過期的驗證",
    headers={"WWW-Authenticate": "Bearer"},
): pass


class InstanceDoesNotExistException(
    HTTPBase,
    status_code=status.HTTP_404_NOT_FOUND,
    detail="實例找不到",
): pass


class AWSClientException(
    HTTPBase,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="上傳作業錯誤，可能因為網路、服務、或權限等等因素",
): pass


class AWSLimitExceededException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="流量超過，請稍後再試",
): pass


class AWSParamValidationException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無效查找",
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
