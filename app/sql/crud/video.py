from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic
from app.exceptions.videos import VideoDoesNotExistException
from app.sql.models.video import video_pydantic, Videos


async def retrieve_video(video_id: int):
    try:
        video = await video_pydantic.from_queryset_single(Videos.get(id=video_id))

    except DoesNotExist:
        raise VideoDoesNotExistException

    return video


async def retrieve_videos():
    return await video_pydantic.from_queryset(Videos.all())


@atomic()
async def create_video(create_object: dict):
    try:
        video = await Videos.create(**create_object)

    # need to add tortoise validation error
    except Exception as e:
        raise e

    return await video_pydantic.from_tortoise_orm(video)


@atomic()
async def update_video(video_id: int, update_object: dict):
    try:
        await Videos.filter(id=video_id).update(**update_object)

    except Exception as e:
        raise e

    return await video_pydantic.from_queryset_single(Videos.get(id=video_id))


@atomic()
async def delete_video(video_id: int) -> None:
    try:
        deleted_count= await Videos.filter(id=video_id).delete()

        if not deleted_count:
            raise DoesNotExist

    except DoesNotExist:
        raise VideoDoesNotExistException
