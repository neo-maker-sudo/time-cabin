from datetime import datetime
from pydantic import BaseModel, Field
from app.enums.video import VideoTypeEnum
from app.utils.general import convert_datetime_format
from app.sql.models.video import video_pydantic


class VideoCreateSchemaIn(BaseModel):
    name: str
    information: str = Field(default="")
    url: str
    type: VideoTypeEnum


class VideoCreateSchemaOut(video_pydantic):
    created_at: datetime
    modified_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, "%Y-%m-%d %H:%M:%S")
        }


class VideoUpdateSchemaIn(BaseModel):
    name: str
    information: str


class VideoUpdateSchemaOut(video_pydantic):
    created_at: datetime
    modified_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, "%Y-%m-%d %H:%M:%S")
        }