from tortoise.exceptions import DoesNotExist
from app.exceptions.auth import LoginInvalidException
from app.sql.models.users import Users


async def retrieve_user_by_email(email: str):
    try:
        user = await Users.get(email=email)

    except DoesNotExist:
        raise LoginInvalidException

    return user
