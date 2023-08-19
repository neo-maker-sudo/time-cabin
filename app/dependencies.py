from fastapi import UploadFile, File, Depends
from app.config import setting
from app.exceptions.users import AvatarFileExtensionException, AvatarFileSizeOverException
from app.exceptions.videos import VideoFileExtensionException
from app.enums.users import AvatarTypeEnum
from app.enums.video import VideoTypeEnum
from app.utils.general import validate_avatar_size
from app.utils.auth.security import verify_access_token


def verify_video_extension(
    upload_file: UploadFile = File(...)
):
    if not upload_file.filename.lower().endswith(VideoTypeEnum.members_tuple()):
        raise VideoFileExtensionException.raise_http_exception()

    return upload_file


def verify_avatar_entension(
    upload_file: UploadFile = File(...),
    user_id: int = Depends(verify_access_token),

) -> dict:
    if not upload_file.filename.lower().endswith(AvatarTypeEnum.members_tuple()):
        raise AvatarFileExtensionException.raise_http_exception()    

    try:
        validate_avatar_size(upload_file.size, setting.AVATAR_MAXIMUM_SIZE)

    except AvatarFileSizeOverException as exc:
        exc.raise_http_exception()

    return {
        "upload_file": upload_file,
        "user_id": user_id,
    }
