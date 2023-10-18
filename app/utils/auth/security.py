import base64
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from time import time
from io import BytesIO
from jose import JWTError, jwt
from fastapi import Cookie
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
import qrcode
from qrcode.image.pure import PyPNGImage
from app.config import setting
from app.exceptions.auth import BearerTokenInvalidException
from app.exceptions.general import JWTUnauthorizeException, InvalidAlgorithm
from app.utils.general import force_bytes


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_access_token(data: dict) -> str:
    payload = data.copy()
    try:
        expired_delta = timedelta(days=setting.JWT_EXPIRE_DAYS)

    except:
        expired_delta = timedelta(days=2)

    exp = datetime.utcnow() + expired_delta 
    payload.update({"exp": exp})

    return (
        setting.COOKIE_ACCESS_TOKEN_TYPE,
        jwt.encode(payload, setting.JWT_SECRET_KEY, setting.JWT_ALGORITHM),
        int(exp.timestamp())
    )


def deconstruct_bearer_token_credentials(access_token: str) -> str:
    scheme, token = get_authorization_scheme_param(access_token)

    if scheme.lower() != setting.COOKIE_ACCESS_TOKEN_TYPE.lower():
        raise BearerTokenInvalidException.raise_http_exception()

    return token


async def verify_access_token(tcat: str = Cookie()):
    token = deconstruct_bearer_token_credentials(tcat)

    try:
        payload = jwt.decode(
            token, setting.JWT_SECRET_KEY, algorithms=[setting.JWT_ALGORITHM]
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


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return secrets.compare_digest(force_bytes(val1), force_bytes(val2))


def salted_hmac(hash_value: str, salt: str, /, *, secret=None, algorithm=None):
    salt_bytes = force_bytes(salt)
    secrets_bytes = force_bytes(secret)
    hash_bytes = force_bytes(hash_value)

    try:
        hasher = getattr(hashlib, algorithm)    

    except AttributeError as e:
        raise InvalidAlgorithm(
            "%r is not an algorithm accepted by the hashlib module" % algorithm
        ) from e

    key = hasher(salt_bytes + secrets_bytes).digest()
    
    return hmac.new(key, msg=hash_bytes, digestmod=hasher)


def generate_2fa_jwt(user_id: int):
    epoch_now = time()

    payload = {
        "iss": setting.AUTHY_APPLICATION_NAME,
        "iat": epoch_now,
        "exp": epoch_now + setting.AUTHY_QRCODE_JWT_TIMEDELTA,
        "context": {
            "custom_user_id": user_id,
            "authy_app_id": setting.AUTHY_APPLICATION_ID
        }
    }

    return jwt.encode(payload, setting.AUTHY_PRODUCTION_API_KEY)


def generate_2fa_qrcode(user_id, /, *, transfer_base64: bool = False) -> str:
    jwt = generate_2fa_jwt(user_id)
    
    qr =  qrcode.make(
        f"authy://account?token={jwt}",
        image_factory=PyPNGImage
    )

    if not transfer_base64:
        return qr

    buffer = BytesIO()
    qr.save(buffer)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')