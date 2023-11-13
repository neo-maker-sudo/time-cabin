from fastapi import status
from .base import HTTPBase


class AvatarFileExtensionException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無效檔案格式"
): pass


class AvatarFileSizeOverException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="超過檔案限制大小"
): pass


class UserUniqueConstraintException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="信箱重複註冊",
): pass


class UserDoesNotExistException(
    HTTPBase,
    status_code=status.HTTP_404_NOT_FOUND,
    detail="使用者不存在",
): pass


class UserOTPCodeIncorrectException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="驗證碼錯誤"
): pass

class UserOTPCodeMisFormatException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="驗證碼格式錯誤"
): pass


class UserEmailNotVerifyException(
    HTTPBase,
    status_code=status.HTTP_403_FORBIDDEN,
    detail="使用者尚未驗證信箱"
): pass
