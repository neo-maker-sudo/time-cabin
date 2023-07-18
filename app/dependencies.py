from fastapi import UploadFile, File
from app.exceptions import VideoFileExtensionException
from app.enums.video import VideoTypeEnum


def verify_video_extension(
    upload_file: UploadFile = File(...)
):
    if not upload_file.filename.lower().endswith(VideoTypeEnum.members_tuple()):
        raise VideoFileExtensionException.raise_http_exception()

    return upload_file