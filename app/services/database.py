from app.config import setting
from app.utils.auth.security import generate_access_token
from app.repositories.database import PostgreSQLRepository
from app.utils.redis import set_oauth_token_into_redis


class UsersService:
    def __init__(self) -> None:
        self.model_name = "Users"
        self.dbs = {
            "postgres": PostgreSQLRepository(setting.DATABASE_CONNECTION)
        }

    async def get_or_create(self, type, /, *, object):
        db = self.dbs.get(type)
        return await db.get_or_create(self.model_name, object)

    async def storage_user_info(self, user, /, *, oauth_access_token, expires_in, request):
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

users_service = UsersService()
