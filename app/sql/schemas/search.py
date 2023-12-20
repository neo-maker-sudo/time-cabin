from pydantic import BaseModel


class AddYoutubePlaylistSchemaIn(BaseModel):
    video_id: str
    playlist_name: str
