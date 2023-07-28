from fastapi import status
from .base import HTTPBase


class LoginInvalidException(
    HTTPBase,
    status_code=status.HTTP_401_UNAUTHORIZED,    
    detail="無效的信箱或密碼"
): pass
