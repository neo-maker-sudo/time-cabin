from fastapi import UploadFile, File
from app.exceptions.users import AvatarFileExtensionException
from app.exceptions.videos import VideoFileExtensionException
from app.enums.users import AvatarTypeEnum
from app.enums.video import VideoTypeEnum


def verify_video_extension(
    upload_file: UploadFile = File(...)
):
    if not upload_file.filename.lower().endswith(VideoTypeEnum.members_tuple()):
        raise VideoFileExtensionException.raise_http_exception()

    return upload_file


def verify_avatar_entension(
    upload_file: UploadFile = File(...)
):
    if not upload_file.filename.lower().endswith(AvatarTypeEnum.members_tuple()):
        raise AvatarFileExtensionException.raise_http_exception()    

    return upload_file
