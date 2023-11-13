from datetime import datetime
from app.repositories.auth import GoogleOauth2Repository
from app.exceptions.auth import (
    OAuth2StateMismatchException,
    OAuth2AccessTokenInvalidGrantException,
    OAuth2UserInfoInvalidGrantException,
)


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
