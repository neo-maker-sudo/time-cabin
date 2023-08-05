from fastapi import status
from .base import HTTPBase


class VideoFileExtensionException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無效檔案格式"
): pass


class VideoNameFieldMaxLengthException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="名稱欄位超過限制長度"
): pass


class VideoDoesNotExistException(
    HTTPBase,
    status_code=status.HTTP_404_NOT_FOUND,
    detail="影片不存在",
): pass
