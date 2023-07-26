from typing import Annotated
from fastapi import APIRouter, UploadFile, Depends, status, Query
from app.dependencies import verify_avatar_entension
from app.exceptions.general import InstanceDoesNotExistException, InstanceFieldException
from app.exceptions.users import UserUniqueConstraintException
from app.sql.crud.users import (
    create_user,
    update_user,
    update_user_avatar,
    retrieve_user,
    delete_user,
    retrieve_user_videos,
)
from app.sql.schemas.users import (
    UserProfileSchemaOut,
    UserCreateSchemaIn,
    UserCreateSchemaOut,
    UserUpdateSchemaIn,
    UserUpdateAvatarSchemaOut,
    UserUpdateSchemaOut,
    UserVideosSchemaOut,
)
from app.utils.security import hash_password, verify_access_token


router = APIRouter(
    prefix="/api",
    tags=["users"]
)


@router.get("/user", response_model=UserProfileSchemaOut)
async def retrieve_user_view(user_id: int = Depends(verify_access_token)):
    try:
        user = await retrieve_user(user_id=user_id)

    except InstanceDoesNotExistException as exc:
        exc.raise_http_exception()
    
    return user 


@router.post("/register", response_model=UserCreateSchemaOut, status_code=status.HTTP_201_CREATED)
async def create_user_view(schema: UserCreateSchemaIn):
    try:
        schema.__dict__["password"] = hash_password(schema.__dict__["password"])
        user = await create_user(schema.dict())

    except UserUniqueConstraintException as exc:
        raise exc.raise_http_exception() 

    return user


@router.patch("/update/user/avatar", response_model=UserUpdateAvatarSchemaOut)
async def update_user_avatar_view(
    user_id: int = Depends(verify_access_token),
    upload_file: UploadFile = Depends(verify_avatar_entension),
):
    try:
        user = await update_user_avatar(user_id, update_object={
            "avatar": upload_file
        })

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
async def delete_user_view(
    user_id: int = Depends(verify_access_token)
):
    try:
        await delete_user(user_id=user_id)

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"


@router.get("/profile/videos", response_model=UserVideosSchemaOut)
async def retrieve_user_videos_view(
    o: Annotated[list[str], Query()] = [],
    user_id: int = Depends(verify_access_token)
):
    try:
        user_videos = await retrieve_user_videos(
            user_id, 
            order_field=(["created_at"] if not o else o ),
        )

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    except InstanceFieldException as exc:
        raise exc.raise_http_exception()

    return user_videos