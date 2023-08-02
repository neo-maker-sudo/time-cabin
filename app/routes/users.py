from typing import Annotated
from fastapi import APIRouter, Depends, status, Query
from fastapi_pagination import add_pagination
from app.dependencies import verify_avatar_entension
from app.exceptions.general import InstanceDoesNotExistException, InstanceFieldException
from app.exceptions.users import UserUniqueConstraintException
from app.exceptions.videos import VideoNameFieldMaxLengthException
from app.sql.crud.users import (
    create_user,
    update_user,
    update_user_avatar,
    retrieve_user,
    delete_user,
    retrieve_user_video,
    retrieve_user_videos,
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
)
from app.sql.schemas.videos import (
    VideoUpdateSchemaIn,
    VideoUpdateSchemaOut,
)
from app.utils.security import hash_password, verify_access_token


router = APIRouter(prefix="/api", tags=["users"])
add_pagination(router)


@router.get("/profile", response_model=UserProfileSchemaOut)
async def retrieve_user_view(user_id: int = Depends(verify_access_token)):
    try:
        user = await retrieve_user(user_id=user_id)

    except InstanceDoesNotExistException as exc:
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

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return user


@router.patch("/update/user", response_model=UserUpdateSchemaOut)
async def update_user_view(
    schema: UserUpdateSchemaIn,
    user_id: int = Depends(verify_access_token),
):
    try:
        user = await update_user(user_id, schema.dict())

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return user


@router.delete("/delete/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_view(user_id: int = Depends(verify_access_token)):
    try:
        await delete_user(user_id=user_id)

    except InstanceDoesNotExistException as exc:
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

    except InstanceDoesNotExistException as exc:
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

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

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

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    except InstanceFieldException as exc:
        raise exc.raise_http_exception()

    return video


@router.delete("/profile/delete/{video_id}/video", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_video_view(
    video_id: int,
    user_id: int = Depends(verify_access_token),
):
    try:
        await delete_user_video(video_id=video_id, user_id=user_id)

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"