from pydantic import BaseModel, Field, EmailStr, validator, parse_obj_as
from app.config import setting


class LoginSchemaIn(BaseModel):
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


class LoginSchemaOut(BaseModel):
    access_token: str
    token_type: str


class AuthyVerifySchemaIn(BaseModel):
    token: str = Field(
        ...,
        min_length=setting.AUTHY_TOKEN_LENGTH,
        max_length=setting.AUTHY_TOKEN_LENGTH,
        regex=setting.AUTHY_TOKEN_REGEX,
        example="12345678",
    )
