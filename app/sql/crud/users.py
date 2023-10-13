import orjson
from asyncpg.exceptions import UniqueViolationError
from tortoise.connection import connections
from tortoise.transactions import atomic
from tortoise.exceptions import IntegrityError, DoesNotExist, FieldError
from tortoise.query_utils import Prefetch
from fastapi_pagination.ext.tortoise import paginate
from app.config import setting
from app.utils.general import urlsave_base64_decode
from app.utils.pagination import VideoParams
from app.exceptions.general import InstanceFieldException
from app.exceptions.users import UserUniqueConstraintException, UserDoesNotExistException
from app.exceptions.videos import VideoNameFieldMaxLengthException, VideoDoesNotExistException
from app.sql.models.users import Users, Authy, users_pydantic
from app.sql.models.video import Videos


async def retrieve_user_by_email(email: str):
    try:
        user = await Users.get(email=email)

    except DoesNotExist:
        raise UserDoesNotExistException

    return user


async def retrieve_user(user_id):
    try:
        user = await Users.get(id=user_id)

    except DoesNotExist:
        raise UserDoesNotExistException

    return user


async def retrieve_user_video(user_id: int, /, *, video_id: int):
    try:
        video = await Videos.get(id=video_id, user_id=user_id)

    except DoesNotExist:
        raise VideoDoesNotExistException

    return video


async def retrieve_user_videos(
    user_id: int, /, *, page: int, size: int, order_field: list
):
    try:
        params = VideoParams(page=page, size=size)

        user = await Users.get(id=user_id).prefetch_related("videos")
        user_videos_pagination = await paginate(
            Videos.filter(user_id=user_id, type__isnull=False, url__isnull=False).order_by(*order_field), 
            params=params
        )
        user.videos.related_objects = user_videos_pagination

    except DoesNotExist:
        raise UserDoesNotExistException

    except FieldError:
        raise InstanceFieldException

    return user


@atomic()
async def create_user(create_object: dict):
    try:
        user = await Users.create(**create_object)

    except IntegrityError as exc:
        if exc.args[0].__class__.__name__ == UniqueViolationError.__name__:
            raise UserUniqueConstraintException

    except Exception as e:
        raise e

    return await users_pydantic.from_tortoise_orm(user)


@atomic()
async def update_user_avatar(user_id: int, avatar_url: str):
    try:
        user = await Users.get(id=user_id)
        user.avatar = avatar_url
        await user.save(update_fields=["avatar", "modified_at"])

    except DoesNotExist:
        raise UserDoesNotExistException

    except Exception as e:
        raise e

    return await Users.get(id=user_id)


@atomic()
async def update_user(user_id: int, update_object: dict):
    try:
        user = await Users.get(id=user_id)
        user.nickname = update_object["nickname"]
        await user.save(update_fields=["nickname", "modified_at"])

    except DoesNotExist:
        raise UserDoesNotExistException

    except Exception as e:
        raise e

    return await Users.get(id=user_id)


@atomic()
async def delete_user(user_id: int) -> None:
    try:
        user = await Users.get(id=user_id)
        await user.delete()

    except DoesNotExist:
        raise UserDoesNotExistException


@atomic()
async def create_user_video(create_object):
    try:
        video = await Videos.create(**create_object)

    except VideoNameFieldMaxLengthException:
        raise VideoNameFieldMaxLengthException

    except Exception as e:
        raise e

    return video


@atomic()
async def insert_user_video(video_id: int, user_id: int, update_object: dict):
    try:
        video = await Videos.get(id=video_id, user_id=user_id)
        video.type = update_object["type"]
        video.url = update_object["url"]
        await video.save(update_fields=["type", "url"])

    except Exception as e:
        raise e


@atomic()
async def update_user_video(video_id: int, user_id: int, update_object: dict):
    conn = connections.get(setting.DATABASE_CONNECTION)

    try:
        command = """
            UPDATE videos
            SET
                modified_at = now(),
                information = $3,
                label = jsonb_set(label, '{tags}', $4, true)
            WHERE id = $1 AND user_id = $2
            RETURNING *;
        """

        qs = await conn.execute_query_dict(
            command,
            [
                video_id,
                user_id,
                update_object["information"],
                orjson.dumps(list(set(update_object["label"]))).decode("utf-8"),
            ]
        )

    except VideoNameFieldMaxLengthException:
        raise VideoNameFieldMaxLengthException

    except DoesNotExist:
        raise VideoDoesNotExistException

    except Exception as e:
        raise e

    return {
        "information": qs[0]["information"],
        "label": orjson.loads(qs[0]["label"])["tags"]
    }


@atomic()
async def delete_user_video(video_id: int, user_id: int):
    try:
        deleted_count= await Videos.filter(id=video_id, user_id=user_id).delete()

        if not deleted_count:
            raise DoesNotExist

    except DoesNotExist:
        raise VideoDoesNotExistException


@atomic()
async def update_user_password(user_id: int, hashed_password: str):
    try:
        user = await Users.get(id=user_id)
        user.password = hashed_password
        await user.save(update_fields=["password", "modified_at"])

    except DoesNotExist:
        raise UserDoesNotExistException

    except Exception as e:
        raise e

    return await Users.get(id=user_id)


async def retrieve_user_by_uidb64(uidb64: str):
    user_id = urlsave_base64_decode(uidb64)
    return await retrieve_user(user_id.decode())


@atomic()
async def reset_user_password(user: Users, hashed_password: str):
    try:
        user.password = hashed_password
        await user.save(update_fields=["password", "modified_at"])

    except Exception as e:
        raise e


async def retrieve_user_with_authy(user_id: int):
    try:
        user = await Users.get(id=user_id).prefetch_related(
            Prefetch("authy", queryset=Authy.filter())
        )

    except DoesNotExist:
        raise UserDoesNotExistException

    return user
