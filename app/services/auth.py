from datetime import datetime
from tortoise.transactions import in_transaction
from app.repositories.auth import GoogleOauth2Repository
from app.repositories.database import AbstractDBRepository
from app.exceptions.auth import (
    OAuth2StateMismatchException,
    OAuth2AccessTokenInvalidGrantException,
    OAuth2UserInfoInvalidGrantException,
)
from app.utils.auth.security import generate_access_token
from app.utils.redis import set_oauth_token_into_redis

async def get_or_create_google_user(repo: AbstractDBRepository, /, *, object):
    with in_transaction() as connection:
        instance = await repo.get_or_create("User", object=object, connection=connection)

    return instance

async def storage_user_info(user, /, *, oauth_access_token, expires_in, request):
    # 使用 user id 產生自己的 access_token
    token_type, access_token, _ = generate_access_token(
        {'user_id': str(user["id"])},
        exp=expires_in,
    )

    # 將自己產生的 token 映射 google token 並附加過期時間存到 redis
    await set_oauth_token_into_redis(
        request.app.state.redis,
        key=access_token,
        value=oauth_access_token,
        expires=expires_in,
    )

    return token_type, access_token


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
