from fastapi import APIRouter, UploadFile, Depends, status
from app.dependencies import verify_avatar_entension
from app.exceptions.general import InstanceDoesNotExistException
from app.exceptions.users import UserUniqueConstraintException
from app.sql.crud.users import (
    create_user,
    update_user,
    update_user_avatar,
    retrieve_user,
    delete_user,
)
from app.sql.schemas.users import (
    UserProfileSchemaOut,
    UserCreateSchemaIn,
    UserCreateSchemaOut,
    UserUpdateSchemaIn,
    UserUpdateAvatarSchemaOut,
    UserUpdateSchemaOut,
)
from app.utils.security import hash_password


router = APIRouter(
    prefix="/api",
    tags=["users"]
)


@router.get("/{user_id}/user", response_model=UserProfileSchemaOut)
async def retrieve_user_view(user_id: int):
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


@router.patch("/update/{user_id}/user/avatar", response_model=UserUpdateAvatarSchemaOut)
async def update_user_avatar_view(
    user_id: int,
    upload_file: UploadFile = Depends(verify_avatar_entension),
):
    try:
        user = await update_user_avatar(user_id, update_object={
            "avatar": upload_file
        })

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return user


@router.patch("/update/{user_id}/user", response_model=UserUpdateSchemaOut)
async def update_user_view(
    user_id: int,
    schema: UserUpdateSchemaIn,
):
    try:
        user = await update_user(user_id, schema.dict())

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return user


@router.delete("/delete/{user_id}/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_view(user_id: int):
    try:
        await delete_user(user_id=user_id)

    except InstanceDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"
