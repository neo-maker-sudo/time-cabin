from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, status, Query, BackgroundTasks
from fastapi_pagination import add_pagination
from app.backgrounds.videos import process_transcoding
from app.dependencies import verify_avatar_entension, verify_video_extension
from app.exceptions.general import InstanceFieldException, PasswordResetInvalidException
from app.exceptions.users import UserUniqueConstraintException, UserDoesNotExistException
from app.exceptions.videos import VideoNameFieldMaxLengthException, VideoDoesNotExistException
from app.sql.crud.users import (
    create_user,
    update_user,
    update_user_avatar,
    update_user_password,
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
    retrieve_mainpage,
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
    MainPageSchemaOut,
)
from app.utils.cloud import upload_file_to_s3
from app.utils.email import email_backend
from app.utils.security import hash_password, verify_access_token
from app.utils.crypto.token import token_generator


router = APIRouter(prefix="/api", tags=["users"])
add_pagination(router)


@router.get("/mainpage", response_model=MainPageSchemaOut)
async def retrieve_mainpage_view():
    videos = await retrieve_mainpage(1, ["-created_at", "-modified_at"])

    return videos


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
    depends_object: dict = Depends(verify_avatar_entension),
):
    try:
        user = await update_user_avatar(
            depends_object["user_id"],
            update_object={"avatar": depends_object["upload_file"]},
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
    user_id: int = Depends(verify_access_token),
):
    filename_folder = upload_file_to_s3(
        upload_file=upload_file,
        user_id=user_id,
    )

    # save into database
    schema = VideoCreateSchemaIn(
        name=form_data.name,
        information=form_data.information,
        user_id=user_id,
    )

    video = await create_user_video(create_object=schema.dict())

    background_task.add_task(
        process_transcoding,
        folder=str(user_id),
        filename=upload_file.filename,
        filename_folder=filename_folder,
        video_id=video.id,
        user_id=user_id,
    )

    return video


@router.patch("/profile/update/{video_id}/video", response_model=VideoUpdateSchemaOut)
async def update_profile_video_view(
    video_id: int,
    schema: VideoUpdateSchemaIn,
    user_id: int = Depends(verify_access_token),
):
    try:
        video = await update_user_video(video_id, user_id, update_object=schema.dict())

    except VideoNameFieldMaxLengthException as exc:
        raise exc.raise_http_exception()

    except VideoDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return video


@router.delete("/profile/delete/{video_id}/video", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_video_view(
    video_id: int,
    user_id: int = Depends(verify_access_token),
):
    try:
        await delete_user_video(video_id=video_id, user_id=user_id)

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
async def reset_user_password_view(schema: PassowrdResetSchemaIn):
    # 查詢 email
    try:
        user = await retrieve_user_by_email(schema.email)

    except UserDoesNotExistException as exc:
        raise exc.raise_http_exception()

    # 生成 token
    token = token_generator.make_token(user)
    # 發送信箱信件，之後可以移到獨立服務去處理
    email_backend.send_mail(token, user)

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
