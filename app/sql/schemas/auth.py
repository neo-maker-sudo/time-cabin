from pydantic import BaseModel, Field, EmailStr, validator, parse_obj_as
from app.config import setting


class LoginSchemaIn(BaseModel):
    email: str = Field(
        ...,
        min_length=setting.USER_EMAIL_FIELD_MIN_LENGTH,
        max_length=setting.USER_EMAIL_FIELD_MAX_LENGTH,
    )
    password: str = Field(
        ...,
        min_length=setting.USER_PASSWORD_FIELD_MIN_LENGTH,
        max_length=setting.USER_PASSWORD_FIELD_MAX_LENGTH,
        regex=setting.PASSWORD_REGEX,
    )

    @validator("email", always=True)
    def check_email(cls, value):
        try:
            parse_obj_as(EmailStr, value)

        except Exception as e:
            raise e

        return value


class LoginSchemaOut(BaseModel):
    access_token: str
    token_type: str
