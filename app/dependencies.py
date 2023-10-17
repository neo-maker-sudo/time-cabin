from fastapi import UploadFile, File, Depends, Query, Request
from app.config import setting
from app.exceptions.users import (
    AvatarFileExtensionException,
    AvatarFileSizeOverException,
    UserOTPCodeIncorrectException,
    UserOTPCodeMisFormatException,
    UserDoesNotExistException,
    UserEmailNotVerifyException,
)
from app.exceptions.videos import VideoFileExtensionException
from app.enums.users import AvatarTypeEnum
from app.enums.video import VideoTypeEnum
from app.utils.general import validate_avatar_size
from app.utils.redis import get_email_verify_otp_from_redis
from app.utils.auth.security import verify_access_token
from app.sql.crud.users import retrieve_user


def verify_video_extension(
    upload_file: UploadFile = File(...)
):
    if not upload_file.filename.lower().endswith(VideoTypeEnum.members_tuple()):
        raise VideoFileExtensionException.raise_http_exception()

    return upload_file


def verify_avatar_extension(
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


async def verify_email_verification_code(
    request: Request,
    code: str = Query(..., min_length=8, max_length=8),
    user_id: str = Depends(verify_access_token),
):
    try:
        int(code)

    except ValueError:
        raise UserOTPCodeMisFormatException.raise_http_exception()

    # Redis 驗證 code
    otp_code = await get_email_verify_otp_from_redis(
        request.app.state.redis,
        user_id=user_id,
    )

    if otp_code != code:
        raise UserOTPCodeIncorrectException.raise_http_exception()

    return user_id


async def verify_user_email_verified(
    user_id: str = Depends(verify_access_token),
):
    try:
        user = await retrieve_user(user_id=user_id)

    except UserDoesNotExistException:
        raise UserDoesNotExistException.raise_http_exception()

    if not user.email_verified:
        raise UserEmailNotVerifyException.raise_http_exception()

    return user
