from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from passlib.context import CryptContext
from app.config import setting
from app.exceptions.general import JWTUnauthorizeException


security_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_access_token(data: dict) -> str:
    payload = data.copy()
    try:
        expired_delta = timedelta(days=setting.JWT_EXPIRE_DAYS)

    except:
        expired_delta = timedelta(days=2)

    exp = datetime.utcnow() + expired_delta 
    payload.update({"exp": exp})

    return jwt.encode(payload, setting.JWT_SECRET_KEY, setting.JWT_ALGORITHM)


def verify_access_token(bear_token: HTTPAuthorizationCredentials = Depends(security_scheme)):
    try:
        payload = jwt.decode(
            bear_token.credentials, setting.JWT_SECRET_KEY, algorithms=[setting.JWT_ALGORITHM]
        )

    except JWTError:
        raise JWTUnauthorizeException.raise_http_exception()

    if not (user_id := payload.get("user_id", None)):
        raise JWTUnauthorizeException.raise_http_exception()
    
    return user_id


def hash_password(plain_password: str):
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
