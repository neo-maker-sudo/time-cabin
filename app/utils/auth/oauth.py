from abc import ABCMeta, abstractmethod
from datetime import datetime
import aiohttp
from fastapi import Request
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError
from app.config import setting
from app.exceptions.auth import (
    OAuth2StateMismatchException,
    OAuth2AccessTokenInvalidGrantException,
    OAuth2UserInfoInvalidGrantException,
)


class Oauth2Repository(object, metaclass=ABCMeta):

    @abstractmethod
    def retrieve_access_token(self):
        raise NotImplemented

    @abstractmethod
    def retrieve_user_info(self):
        raise NotImplemented


class GoogleOauth2Repository(Oauth2Repository):
    # https://blog.csdn.net/qq_35952638/article/details/101567198
    # https://stackoverflow.com/questions/55448883/how-i-can-get-user-info-profile-from-google-api

    TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"
    TOKEN_HEADERS = dict = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    CLIENT_TIMEOUT = aiohttp.ClientTimeout(total=3)

    def parse_request_uri_response(self, uri: str, state: str) -> str:
        try:
            code = setting.GOOGLE_OAUTH_CLIENT.parse_request_uri_response(uri, state=state).get("code")

        except MismatchingStateError:
            raise OAuth2StateMismatchException

        return code

    def prepare_request_body(self, code, redirect_uri) -> str:
        return setting.GOOGLE_OAUTH_CLIENT.prepare_request_body(
            code=code,
            redirect_uri=redirect_uri,
            client_secret=setting.GOOGLE_CLIENT_SECRET,
        )

    async def _retrieve_token(self, body):
        async with aiohttp.ClientSession(timeout=self.CLIENT_TIMEOUT) as session:
            async with session.post(self.TOKEN_URL, data=body, headers=self.TOKEN_HEADERS) as resp:
                response = await resp.json()

        if response.get("error", None):
            raise OAuth2AccessTokenInvalidGrantException

        return response

    async def retrieve_access_token(self, uri: str, state: str, /, *, request: Request):
        code = self.parse_request_uri_response(uri, state)

        body = self.prepare_request_body(
            code,
            redirect_uri=request.url_for(setting.GOOGLE_CALLBACK_ROUTE_NAME),
        )

        return await self._retrieve_token(body)

    async def retrieve_user_info(self, token_type: str, access_token: str):
        headers = {"Authorization": f"{token_type} {access_token}"}

        async with aiohttp.ClientSession(timeout=self.CLIENT_TIMEOUT) as session:
            async with session.get(self.USER_INFO_URL, headers=headers) as resp:
                response = await resp.json()

        if response.get("error", None):
            raise OAuth2UserInfoInvalidGrantException

        return response


# service layer 不需要關心資料如何取得或存取
class OAuth2Service:
    def __init__(self) -> None:
        self.repositories = {
            "google": GoogleOauth2Repository()
        }

    async def login(self, repository: str, schema, request):
        repo = self.repositories.get(repository, None)

        try:

            # 拿已經有授權完成的 uri 與 state 去取得 code
            response = await repo.retrieve_access_token(schema.uri, schema.state, request=request)

            # 拿 token 去取得 user info
            user_info = await repo.retrieve_user_info(
                token_type=response["token_type"],
                access_token=response["access_token"],
            )

        except OAuth2StateMismatchException as exc:
            raise exc.raise_http_exception()

        except (OAuth2AccessTokenInvalidGrantException, OAuth2UserInfoInvalidGrantException) as exc:
            raise exc.raise_http_exception()

        return (
            user_info,
            response["access_token"],
            int(datetime.now().timestamp()) + response["expires_in"]
        )


oauth2_service = OAuth2Service()
