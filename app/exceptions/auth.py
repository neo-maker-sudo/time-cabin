from fastapi import status
from .base import HTTPBase


class LoginInvalidException(
    HTTPBase,
    status_code=status.HTTP_401_UNAUTHORIZED,    
    detail="無效的信箱、密碼或錯誤的登入方式"
): pass


class AuthyUnregisteredException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="尚未註冊兩階段驗證帳號",
): pass


class AuthyVerifyException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="驗證碼錯誤或無效，請重新嘗試",    
): pass


class AuthyConnectionException(
    HTTPBase,
    status_code=status.HTTP_417_EXPECTATION_FAILED,
    detail="網路連線錯誤，請重試",
): pass


class BearerTokenInvalidException(
    HTTPBase,
    status_code=status.HTTP_403_FORBIDDEN,
    detail="身份驗證錯誤或無效",
): pass


class OAuth2AccessTokenInvalidGrantException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無效請求（OATIG）"
): pass


class OAuth2UserInfoInvalidGrantException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無效請求（OUIIG）"
): pass


class OAuth2StateMismatchException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="錯誤或是無效的參數"
): pass
