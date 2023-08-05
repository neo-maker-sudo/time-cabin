from datetime import datetime
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, validator, parse_obj_as
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
    email: str = Field(
        ...,
        min_length=setting.USER_EMAIL_FIELD_MIN_LENGTH,
        max_length=setting.USER_EMAIL_FIELD_MAX_LENGTH,
        example="user@example.com",
    )
    password: str = Field(
        ...,
        min_length=setting.USER_PASSWORD_FIELD_MIN_LENGTH,
        max_length=setting.USER_PASSWORD_FIELD_MAX_LENGTH,
        regex=setting.PASSWORD_REGEX,
        example="Aa12345678",
    )

    @validator("email", always=True)
    def check_email(cls, value):
        try:
            parse_obj_as(EmailStr, value)

        except Exception as e:
            raise e

        return value


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
    nickname: str = Field(
        ...,
        min_length=setting.USER_NICKNAME_FIELD_MIN_LENGTH,
        max_length=setting.USER_NICKNAME_FIELD_MAX_LENGTH,
    )


class UserUpdateSchemaOut(user_update_pydantic):
    ...


class UserVideoCreateFormSchema:
    def __init__(
        self,
        name: str = Form(
            ...,
            min_length=setting.VIDEO_NAME_FIELD_MIN_LENGTH,
            max_length=setting.VIDEO_NAME_FIELD_MAX_LENGTH
        ),
        information: str = Form()
    ):
        self.name = name
        self.information = information


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