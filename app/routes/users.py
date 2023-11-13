from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, status, Query, BackgroundTasks, Request
from fastapi_pagination import add_pagination
from app.backgrounds.videos import process_transcoding
from app.backgrounds.email import send_reset_password_email, send_user_verify_email
from app.dependencies import (
    verify_avatar_extension,
    verify_video_extension,
    verify_email_verification_code,
    verify_user_email_verified,
)
from app.exceptions.general import InstanceFieldException, PasswordResetInvalidException
from app.exceptions.users import UserUniqueConstraintException, UserDoesNotExistException
from app.exceptions.videos import VideoNameFieldMaxLengthException, VideoDoesNotExistException
from app.sql.crud.users import (
    create_user,
    update_user,
    update_user_avatar,
    update_user_password,
    update_user_email_verified,
    reset_user_password,
    retrieve_user,
    retrieve_user_by_email,
    retrieve_user_by_uidb64,
    delete_user,
    retrieve_user_video,
    retrieve_user_videos,
    create_user_video,
    update_user_video,
    delete_user_video,
)
from app.sql.schemas.users import (
    UserProfileSchemaOut,
    UserCreateSchemaIn,
    UserCreateSchemaOut,
    UserUpdateSchemaIn,
    UserUpdateAvatarSchemaOut,
    UserUpdateSchemaOut,
    UserVideoSchemaOut,
    UserVideosSchemaOut,
    UserVideoCreateFormSchema,
    ChangePasswordSchemaIn,
    PassowrdResetSchemaIn,
    PasswordResetConfirmSchemaIn,
)
from app.sql.schemas.videos import (
    VideoCreateSchemaIn,
    VideoCreateSchemaOut,
    VideoUpdateSchemaIn,
    VideoUpdateSchemaOut,
)
from app.utils.cloud import upload_file_to_s3
from app.utils.email import user_verify_email_backend
from app.utils.redis import set_email_verify_otp_into_redis, set_email_verify_otp_expired
from app.utils.auth.security import hash_password, verify_access_token
from app.utils.crypto.token import token_generator


router = APIRouter(prefix="/api", tags=["users"])
add_pagination(router)


@router.get("/profile", response_model=UserProfileSchemaOut)
async def retrieve_user_view(user_id: int = Depends(verify_access_token)):
    try:
        user = await retrieve_user(user_id=user_id)

    except UserDoesNotExistException as exc:
        exc.raise_http_exception()

    return user


@router.post(
    "/register", response_model=UserCreateSchemaOut, status_code=status.HTTP_201_CREATED
)
async def create_user_view(schema: UserCreateSchemaIn):
    try:
        schema.__dict__["password"] = hash_password(schema.__dict__["password"])
        user = await create_user(schema.dict())

    except UserUniqueConstraintException as exc:
        raise exc.raise_http_exception()

    return user


@router.patch("/update/user/avatar", response_model=UserUpdateAvatarSchemaOut)
async def update_user_avatar_view(
    depends_object: dict = Depends(verify_avatar_extension),
):
    # 上傳照片到 aws s3
    avatar_url = upload_file_to_s3(
        depends_object["upload_file"],
        depends_object["user_id"],
        prefix="avatars",
        nested_sub_folder=False,
    )

    # 更新 avatar link 到 db
    try:
        user = await update_user_avatar(
            depends_object["user_id"],
            avatar_url=avatar_url,
        )

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return user


@router.patch("/update/user", response_model=UserUpdateSchemaOut)
async def update_user_view(
    schema: UserUpdateSchemaIn,
    user_id: int = Depends(verify_access_token),
):
    try:
        user = await update_user(user_id, schema.dict())

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return user


@router.delete("/delete/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_view(user_id: int = Depends(verify_access_token)):
    try:
        await delete_user(user_id=user_id)

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"


@router.get("/profile/videos", response_model=UserVideosSchemaOut)
async def retrieve_user_videos_view(
    page: int = Query(ge=1),
    size: int = Query(ge=1),
    o: Annotated[list[str], Query()] = [],
    user_id: int = Depends(verify_access_token),
):
    try:
        user_videos = await retrieve_user_videos(
            user_id,
            page=page,
            size=size,
            order_field=(["-created_at"] if not o else o),
        )

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    except InstanceFieldException as exc:
        raise exc.raise_http_exception()

    return user_videos


@router.get("/profile/{video_id}/video", response_model=UserVideoSchemaOut)
async def retrieve_profile_video_view(
    video_id: int,
    user_id: int = Depends(verify_access_token),
):
    try:
        video = await retrieve_user_video(user_id, video_id=video_id)

    except VideoDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return video


@router.post("/profile/create/video", status_code=status.HTTP_201_CREATED, response_model=VideoCreateSchemaOut)
async def create_user_video_view(
    background_task: BackgroundTasks,
    upload_file: UploadFile = Depends(verify_video_extension),
    form_data: UserVideoCreateFormSchema = Depends(),
    user = Depends(verify_user_email_verified),
):
    filename_folder = upload_file_to_s3(
        upload_file=upload_file,
        user_id=user.user_id,
        prefix="videos"
    )

    # save into database
    schema = VideoCreateSchemaIn(
        label={
            "tags": list(set(form_data.video_tags[0].split(",")))
        },
        information=form_data.information,
        user_id=user.user_id,
    )

    video = await create_user_video(create_object=schema.dict())

    background_task.add_task(
        process_transcoding,
        folder=str(user.user_id),
        filename=upload_file.filename,
        filename_folder=filename_folder,
        video_id=video.id,
        user_id=user.user_id,
    )

    return video


@router.patch("/profile/update/{video_id}/video", response_model=VideoUpdateSchemaOut)
async def update_profile_video_view(
    video_id: int,
    schema: VideoUpdateSchemaIn,
    user = Depends(verify_user_email_verified),
):
    try:
        video = await update_user_video(video_id, user.user_id, update_object=schema.dict())

    except VideoNameFieldMaxLengthException as exc:
        raise exc.raise_http_exception()

    except VideoDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return video


@router.delete("/profile/delete/{video_id}/video", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_video_view(
    video_id: int,
    user = Depends(verify_user_email_verified),
):
    try:
        await delete_user_video(video_id=video_id, user_id=user.user_id)

    except VideoDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"


@router.patch("/change/password")
async def change_user_password_view(
    schema: ChangePasswordSchemaIn,
    user_id: int = Depends(verify_access_token),
):
    hashed_password = hash_password(schema.password)
    try:
        await update_user_password(user_id, hashed_password=hashed_password)

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"


@router.patch("/reset/password")
async def reset_user_password_view(
    background_task: BackgroundTasks,
    schema: PassowrdResetSchemaIn,
):
    try:
        user = await retrieve_user_by_email(schema.email)

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    # 生成 token
    token = token_generator.make_token(user)

    # 發送信箱信件
    background_task.add_task(
        send_reset_password_email,
        token=token,
        user_id=user.id,
        email=user.email,
    )

    return "OK"


@router.patch("/reset/password/confirm")
async def reset_user_password_confirm_view(schema: PasswordResetConfirmSchemaIn):
    try:
        user = await retrieve_user_by_uidb64(schema.uid)

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    if not token_generator.verify_token(user, schema.token):
        raise PasswordResetInvalidException.raise_http_exception()

    hashed_password = hash_password(schema.new_password)
    await reset_user_password(user, hashed_password=hashed_password)

    return "OK"


@router.get("/email-verification", status_code=status.HTTP_200_OK)
async def send_email_verification(
    background_task: BackgroundTasks,
    request: Request,
    user_id: int = Depends(verify_access_token)
):
    # 驗證使用者是否存在
    try:
        user = await retrieve_user(user_id=user_id)

    except UserDoesNotExistException as exc:
        exc.raise_http_exception()

    # 確認使用者是否驗證過
    if not user.email_verified:
        # 產生 OTP 驗證碼
        code = user_verify_email_backend.generate_otp_code()

        # 存入 Redis
        await set_email_verify_otp_into_redis(
            request.app.state.redis,
            user_id=user_id,
            value=code,
        )

        # 如果沒驗證過發送驗證信
        background_task.add_task(
            send_user_verify_email,
            email=user.email,
            code=code,
        )

        return {"send_mail": True}

    return {"send_mail": None}


@router.patch("/email-verification", status_code=status.HTTP_200_OK)
async def send_email_verification(
    request: Request,
    user_id: str = Depends(verify_email_verification_code),
):
    # 修改使用者 db 狀態
    try:
        await update_user_email_verified(user_id)

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    await set_email_verify_otp_expired(
        request.app.state.redis,
        user_id=user_id,
    )

    return "OK"
