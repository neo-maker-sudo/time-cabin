from app.repositories.search import AbstractSearchRepository


def search_videos(repo: AbstractSearchRepository, q: str, page_token: str):
    return repo.search(q, page_token)


def get_video(repo: AbstractSearchRepository, video_id: str):
    return repo.get(video_id)