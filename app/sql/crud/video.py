from tortoise.exceptions import DoesNotExist
from app.exceptions.general import InstanceDoesNotExistException
from app.sql.models.video import video_pydantic, Videos


async def retrieve_video(video_id: int):
    try:
        video = await video_pydantic.from_queryset_single(Videos.get(id=video_id))

    except DoesNotExist:
        raise InstanceDoesNotExistException

    return video


async def retrieve_videos():
    return await video_pydantic.from_queryset(Videos.all())


async def create_video(create_object: dict):
    try:
        video = await Videos.create(**create_object)

    # need to add tortoise validation error
    except Exception as e:
        raise e

    return await video_pydantic.from_tortoise_orm(video)


async def update_video(video_id: int, update_object: dict):
    try:
        await Videos.filter(id=video_id).update(**update_object)

    # need to add tortoise validation error
    except Exception as e:
        raise e

    return await video_pydantic.from_queryset_single(Videos.get(id=video_id))


async def delete_video(video_id: int) -> None:
    try:
        deleted_count= await Videos.filter(id=video_id).delete()

        if not deleted_count:
            raise DoesNotExist

    except DoesNotExist:
        raise InstanceDoesNotExistException