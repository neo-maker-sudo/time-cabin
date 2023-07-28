from fastapi import status
from .base import HTTPBase


class VideoFileExtensionException(
    HTTPBase,
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="無效檔案格式"
): pass
