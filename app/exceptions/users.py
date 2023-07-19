from fastapi import status
from .base import HTTPBase


class AvatarFileExtensionException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="invalid file extension"
): pass


class UserUniqueConstraintException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="信箱重複註冊",
): pass
