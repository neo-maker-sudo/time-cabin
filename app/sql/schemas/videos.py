from datetime import datetime
from pydantic import BaseModel, Field
from app.config import setting
from app.utils.general import convert_datetime_format
from app.sql.models.video import video_pydantic, video_update_pydantic, mainpage_pydantic


class VideoCreateSchemaIn(BaseModel):
    label: dict
    information: str = Field(default="")
    url: str = Field(None)
    type: str = Field(None)
    user_id: str


class VideoCreateSchemaOut(video_pydantic):
    created_at: datetime
    modified_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, setting.DATE_TIME_FORMAT)
        }


class VideoUpdateSchemaIn(BaseModel):
    label: list[str] = Field(
        None,
        max_length=setting.VIDEO_LABEL_FIELD_VIDEO_TAG_MAX_LENGTH,
    )
    information: str = Field(...)


class VideoUpdateSchemaOut(BaseModel):
    label: list[str] = []
    information: str


class MainPageSchemaOut(BaseModel):
    items: list[mainpage_pydantic] = []
    total: int
    page: int
    size: int
    pages: int
