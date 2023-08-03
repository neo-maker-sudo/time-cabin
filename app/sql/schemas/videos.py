from datetime import datetime
from pydantic import BaseModel, Field
from app.config import setting
from app.utils.general import convert_datetime_format
from app.sql.models.video import video_pydantic, video_update_pydantic


class VideoCreateSchemaIn(BaseModel):
    name: str
    information: str = Field(default="")
    url: str = Field(None)
    type: str = Field(None)
    user_id: int


class VideoCreateSchemaOut(video_pydantic):
    created_at: datetime
    modified_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, setting.DATE_TIME_FORMAT)
        }


class VideoUpdateSchemaIn(BaseModel):
    name: str = Field(..., min_length=setting.VIDEO_NAME_FIELD_MIN_LENGTH, max_length=setting.VIDEO_NAME_FIELD_MAX_LENGTH)
    information: str = Field(...)


class VideoUpdateSchemaOut(video_update_pydantic):
    ...
