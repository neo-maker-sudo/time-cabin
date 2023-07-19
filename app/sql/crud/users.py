from asyncpg.exceptions import UniqueViolationError
from tortoise.exceptions import IntegrityError, DoesNotExist
from app.exceptions.general import InstanceDoesNotExistException
from app.exceptions.users import UserUniqueConstraintException
from app.sql.models.users import Users, users_pydantic


async def retrieve_user(user_id):
    try:
        user = await Users.get(id=user_id)

    except DoesNotExist:
        raise InstanceDoesNotExistException

    return user


async def create_user(create_object: dict):
    try:
        user = await Users.create(**create_object)

    # need to add tortoise validation error
    except IntegrityError as exc:
        if exc.args[0].__class__.__name__ == UniqueViolationError.__name__:
            raise UserUniqueConstraintException

    except Exception as e:
        raise e

    return await users_pydantic.from_tortoise_orm(user)


async def update_user_avatar(user_id: int, update_object: dict):
    try:
        user = await Users.get(id=user_id)
        user.avatar = update_object["avatar"]
        await user.save(update_fields=["avatar"])

    except DoesNotExist:
        raise InstanceDoesNotExistException

    return await users_pydantic.from_queryset_single(Users.get(id=user_id))


async def update_user(user_id: int, update_object: dict):
    try:
        await Users.filter(id=user_id).update(**update_object)

    except DoesNotExist:
        raise InstanceDoesNotExistException

    return await users_pydantic.from_queryset_single(Users.get(id=user_id))


async def delete_user(user_id: int) -> None:
    try:
        user = await Users.get(id=user_id)
        await user.delete()

    except DoesNotExist:
        raise InstanceDoesNotExistException
