import re
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, validator, parse_obj_as, root_validator
from app.config import setting
from app.enums.general import ChangedPasswordLengthEnum
from app.exceptions.general import (
    PasswordEmptyException,
    ChangePasswordEqualException,
    ChangePasswordInvalidException,
    ChangePasswordNotMatchException,
)
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
        video_tags: list[str] = Form(
            max_length=setting.VIDEO_LABEL_FIELD_VIDEO_TAG_MAX_LENGTH,
        ),
        information: str = Form()
    ):
        self.video_tags = video_tags
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
    tags: list[str] = []
    information: str
    url: str


class ChangePasswordSchemaIn(BaseModel):
    old_password: str = Field(
        ...,
        min_length=ChangedPasswordLengthEnum.PasswordMinLength,
        max_length=ChangedPasswordLengthEnum.PasswordMaxLength,
    )
    new_password: str = Field(
        ...,
        min_length=ChangedPasswordLengthEnum.PasswordMinLength,
        max_length=ChangedPasswordLengthEnum.PasswordMaxLength,
    )
    confirm_password: str= Field(
        ...,
        min_length=ChangedPasswordLengthEnum.PasswordMinLength,
        max_length=ChangedPasswordLengthEnum.PasswordMaxLength,
    )

    @root_validator(pre=True)
    def validate_password(cls, values):
        pw1 = values.get("old_password", None)
        pw2 = values.get("new_password", None)
        pw3 = values.get("confirm_password", None)

        if not re.findall(setting.PASSWORD_REGEX, pw2):
            raise ChangePasswordInvalidException.raise_http_exception()

        elif pw1 is None or pw2 is None or pw3 is None:
            raise PasswordEmptyException.raise_http_exception()

        elif pw1 == pw2:
            raise ChangePasswordEqualException.raise_http_exception()

        elif pw2 is not None and pw3 is not None and pw2 != pw3:
            raise ChangePasswordNotMatchException.raise_http_exception()
        
        return values


class PassowrdResetSchemaIn(BaseModel):
    email: EmailStr = Field(...)


class PasswordResetConfirmSchemaIn(BaseModel):
    uid: str = Field(...)
    token: str = Field(...)
    new_password: str = Field(
        ...,
        min_length=ChangedPasswordLengthEnum.PasswordMinLength,
        max_length=ChangedPasswordLengthEnum.PasswordMaxLength,
    )
    confirm_password: str= Field(
        ...,
        min_length=ChangedPasswordLengthEnum.PasswordMinLength,
        max_length=ChangedPasswordLengthEnum.PasswordMaxLength,
    )

    @root_validator(pre=True)
    def validate_password(cls, values):
        pw1 = values.get("new_password", None)
        pw2 = values.get("confirm_password", None)

        if not re.findall(setting.PASSWORD_REGEX, pw1):
            raise ChangePasswordInvalidException.raise_http_exception()

        elif pw1 is None or pw2 is None:
            raise PasswordEmptyException.raise_http_exception()

        elif pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ChangePasswordNotMatchException.raise_http_exception()
        
        return values
