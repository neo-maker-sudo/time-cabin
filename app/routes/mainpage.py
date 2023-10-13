from fastapi import APIRouter, Query
from app.exceptions.general import SearchVideosOperationException
from app.sql.crud.mainpage import search_videos


router = APIRouter(
    prefix="",
    tags=["mainpage"]
)


@router.get("/search")
async def test_view(
    tag: str = Query(),
    page: int = Query(ge=1),
):
    try:
        qs = await search_videos(tag, page)

    except SearchVideosOperationException as exc:
        raise exc.raise_http_exception()

    return qs
