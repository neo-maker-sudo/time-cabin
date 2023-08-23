from authy.api import AuthyApiClient
from requests.exceptions import ConnectionError
from app.config import setting
from app.exceptions.auth import (
    AuthyUnregisteredException,
    AuthyVerifyException,
    AuthyConnectionException,
)


authy_api = AuthyApiClient(setting.AUTHY_PRODUCTION_API_KEY)


def verify_token(user_authy_id: int, token: str) -> None:
    try:
        verification = authy_api.tokens.verify(user_authy_id, token=token)

        if not verification.ok():
            raise AuthyVerifyException

    except ConnectionError:
        raise AuthyConnectionException

    except Exception as e:
        raise e


def disable_registration(user_authy_id: int) -> None:
    try:
        deleted = authy_api.users.delete(user_authy_id)

        if not deleted.ok():
            raise AuthyUnregisteredException

    except ConnectionError:
        raise AuthyConnectionException

    except Exception as e:
        raise e


def registration_status(user_id: int):
    try:
        res = authy_api.users.registration_status(user_id)

        if not res.ok():
            raise AuthyUnregisteredException

    except ConnectionError:
        raise AuthyConnectionException

    except Exception as e:
        raise e

    return res.content