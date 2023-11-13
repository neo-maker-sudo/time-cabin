from tortoise import connections
from tortoise.exceptions import OperationalError
from app.config import setting
from app.exceptions.general import SearchVideosOperationException


async def search_videos(tag: str, page: int):
    conn = connections.get("default")
    command = """
    SELECT
        id,
        url,
        created_at,
        information,
        likes
    FROM videos
    WHERE to_tsvector('simple', label ->> 'tags') @@ to_tsquery($1) AND url IS NOT NULL AND type IS NOT NULL
    ORDER BY created_at DESC, likes DESC
    LIMIT $2 OFFSET $3;
    """

    try:
        qs = await conn.execute_query_dict(
            command,
            [
                f"{tag}:*",
                setting.MAINPAGE_PAGINATION_SIZE,
                (page - 1) * setting.MAINPAGE_PAGINATION_SIZE
            ]
        )

    except OperationalError:
        raise SearchVideosOperationException

    return qs