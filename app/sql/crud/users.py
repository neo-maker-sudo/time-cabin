from asyncpg.exceptions import UniqueViolationError
from tortoise.exceptions import IntegrityError, DoesNotExist, FieldError
from tortoise.query_utils import Prefetch
from fastapi_pagination.ext.tortoise import paginate
from app.utils.pagination import VideoParams
from app.exceptions.general import InstanceDoesNotExistException, InstanceFieldException
from app.exceptions.users import UserUniqueConstraintException
from app.exceptions.videos import VideoNameFieldMaxLengthException
from app.sql.models.users import Users, users_pydantic
from app.sql.models.video import Videos


async def retrieve_user(user_id):
    try:
        user = await Users.get(id=user_id)

    except DoesNotExist:
        raise InstanceDoesNotExistException

    return user


async def retrieve_user_video(user_id: int, /, *, video_id: int):
    try:
        video = await Videos.get(id=video_id, user_id=user_id)

    except DoesNotExist:
        raise InstanceDoesNotExistException

    return video


async def retrieve_user_videos(
    user_id: int, /, *, page: int, size: int, order_field: list
):
    try:
        params = VideoParams(page=page, size=size)

        if not (
            qs := await Users.get(id=user_id).prefetch_related(
                Prefetch("videos", queryset=Videos.filter())
            )
        ):
            raise DoesNotExist

    except DoesNotExist:
        raise InstanceDoesNotExistException

    except FieldError:
        raise InstanceFieldException

    user_videos_pagination = await paginate(
        qs.videos.order_by(*order_field), params=params
    )
    qs.videos.related_objects = user_videos_pagination
    return qs


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

    except Exception as e:
        raise e

    return await Users.get(id=user_id)


async def update_user(user_id: int, update_object: dict):
    try:
        await Users.filter(id=user_id).update(**update_object)

    except DoesNotExist:
        raise InstanceDoesNotExistException

    except Exception as e:
        raise e

    return await Users.get(id=user_id)


async def delete_user(user_id: int) -> None:
    try:
        user = await Users.get(id=user_id)
        await user.delete()

    except DoesNotExist:
        raise InstanceDoesNotExistException


async def create_user_video(create_object):
    try:
        video = await Videos.create(**create_object)

    except VideoNameFieldMaxLengthException:
        raise VideoNameFieldMaxLengthException

    except Exception as e:
        raise e

    return video


async def insert_user_video(video_id: int, user_id: int, update_object: dict):
    try:
        video = await Videos.get(id=video_id, user_id=user_id)
        video.type = update_object["type"]
        video.url = update_object["url"]
        await video.save(update_fields=["type", "url"])

    except Exception as e:
        raise e


async def update_user_video(video_id: int, user_id: int, update_object: dict):
    try:
        video = await Videos.get(id=video_id, user_id=user_id)
        video.name = update_object["name"]
        video.information = update_object["information"]
        await video.save(update_fields=["name", "information"])

    except VideoNameFieldMaxLengthException:
        raise VideoNameFieldMaxLengthException

    except DoesNotExist:
        raise InstanceDoesNotExistException

    except FieldError:
        raise InstanceFieldException

    except Exception as e:
        raise e

    return video


async def delete_user_video(video_id: int, user_id: int):
    try:
        deleted_count= await Videos.filter(id=video_id, user_id=user_id).delete()

        if not deleted_count:
            raise DoesNotExist

    except DoesNotExist:
        raise InstanceDoesNotExistException