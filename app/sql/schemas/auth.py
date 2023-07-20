from pydantic import BaseModel, Field, EmailStr
from app.config import setting


class LoginSchemaIn(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., regex=setting.PASSWORD_REGEX)


class LoginSchemaOut(BaseModel):
    access_token: str
    token_type: str
