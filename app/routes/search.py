from fastapi import APIRouter, Query, Depends
from app.repositories.search import YoutubeSearchRepository
from app.repositories.database import PostgreSQLRepository
from app import services
from app.exceptions.search import (
    RequestsTimeoutException,
    RequestsHttpErrorException,
    RequestsInvalidException,
)
from app.exceptions.videos import PlaylistDoesNotExistException
from app.utils.auth.security import verify_access_token
from app.sql.schemas.search import AddYoutubePlaylistSchemaIn

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/youtube/videos")
def retrieve_youtube_videos_view(q: str = Query(...), page_token: str = Query(default=None)):
    try:
        repo = YoutubeSearchRepository()
        videos = services.search_videos(repo, q=q, page_token=page_token)

    except RequestsTimeoutException as exc:
        raise exc.raise_http_exception()

    except RequestsHttpErrorException as exc:
        raise exc.raise_http_exception()

    except RequestsInvalidException as exc:
        raise exc.raise_http_exception()

    return {
        "page_token": videos["nextPageToken"],
        "list": [
            {
                "title": item["snippet"]["title"],
                "image": item["snippet"]["thumbnails"]["medium"]["url"],
                "video_id": item['id']['videoId'],
                "video_url": f"https://www.youtube.com/embed/{item['id']['videoId']}"
            }
            for item in videos["items"]
        ]
    }

@router.post("/youtube/playlist/add")
async def add_youtube_playlist_view(schema: AddYoutubePlaylistSchemaIn, user_id: int = Depends(verify_access_token),):
    try:
        repo = YoutubeSearchRepository()
        video = services.get_video(repo, video_id=schema.video_id)

    except RequestsTimeoutException as exc:
        raise exc.raise_http_exception()

    except RequestsHttpErrorException as exc:
        raise exc.raise_http_exception()

    except RequestsInvalidException as exc:
        raise exc.raise_http_exception()

    await services.add_video(
        PostgreSQLRepository(),
        playlist_name=schema.playlist_name,
        object={
            "identifier_code": video["items"][0]["id"],
            "title": video["items"][0]["snippet"]["title"],
            "image": video["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
            "url": f"https://www.youtube.com/embed/{video['items'][0]['id']}",
            "user_id": user_id
        }
    )

    return "OK"

@router.post("/youtube/playlist/edit")
async def edit_youtube_playlist_view(schema: AddYoutubePlaylistSchemaIn, user_id: int = Depends(verify_access_token)):
    try:
        repo = YoutubeSearchRepository()
        video = services.get_video(repo, video_id=schema.video_id)

    except RequestsTimeoutException as exc:
        raise exc.raise_http_exception()

    except RequestsHttpErrorException as exc:
        raise exc.raise_http_exception()

    except RequestsInvalidException as exc:
        raise exc.raise_http_exception()

    try:
        await services.edit_video(
            PostgreSQLRepository(),
            playlist_name=schema.playlist_name,
            object={
                "identifier_code": video["items"][0]["id"],
                "title": video["items"][0]["snippet"]["title"],
                "image": video["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
                "url": f"https://www.youtube.com/embed/{video['items'][0]['id']}",
                "user_id": user_id,
            }
        )

    except PlaylistDoesNotExistException as exc:
        raise exc.raise_http_exception()

    return "OK"
