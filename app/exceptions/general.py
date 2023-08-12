from fastapi import status
from .base import HTTPBase


class JWTUnauthorizeException(
    HTTPBase,
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="無效或過期的驗證",
    headers={"WWW-Authenticate": "Bearer"},
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
    detail="排序欄位不存在",
    status_code=status.HTTP_400_BAD_REQUEST,
): pass


class ChangePasswordInvalidException(
    HTTPBase,
    detail="密碼至少需要一個數字、一個大寫、一個小寫",
    status_code=status.HTTP_400_BAD_REQUEST,        
): pass


class ChangePasswordNotMatchException(
    HTTPBase,
    detail="密碼與確認密碼不符合",
    status_code=status.HTTP_400_BAD_REQUEST,
): pass


class InvalidAlgorithm(ValueError):
    """Algorithm is not supported by hashlib."""
    pass


class EmailEncryptSetupException(ValueError):
    def __init__(self, *args: object) -> None:
        self.message = "EMAIL_USE_TLS 與 EMAIL_USE_SSL 是互斥的，只需要設定其中一個為 True"
        super().__init__(*args)
