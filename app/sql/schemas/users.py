from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.config import setting
from app.utils.general import convert_datetime_format
from app.sql.models.users import users_pydantic, users_videos_pydantic, user_update_pydantic, user_avatar_pydantic
from app.sql.schemas.videos import video_pydantic

class UserProfileSchemaOut(users_pydantic):
    created_at: datetime
    modified_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, setting.DATE_TIME_FORMAT)
        }


class UserCreateSchemaIn(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., regex=setting.PASSWORD_REGEX, example="Aa12345678")


class UserCreateSchemaOut(users_pydantic):
    created_at: datetime
    modified_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, setting.DATE_TIME_FORMAT)
        }


class UserUpdateAvatarSchemaOut(user_avatar_pydantic):
    ...


class UserUpdateSchemaIn(BaseModel):
    nickname: str = Field(..., max_length=64)


class UserUpdateSchemaOut(user_update_pydantic):
    ...


class UserVideosPaginationSchema(BaseModel):
    items: list[video_pydantic] = []
    total: int | None = None
    pages: int | None = None
    page: int | None = None
    size: int | None = None


class UserVideosSchemaOut(users_videos_pydantic):
    videos: UserVideosPaginationSchema

    class Config:
        json_encoders = {
            datetime: lambda datetime: convert_datetime_format(datetime, setting.DATE_TIME_FORMAT)
        }


class UserVideoSchemaOut(BaseModel):
    name: str
    information: str
    url: str