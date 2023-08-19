from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic
from tortoise.query_utils import Prefetch
from app.exceptions.auth import LoginInvalidException, AuthyUnregisteredException
from app.sql.models.users import Users, Authy


async def retrieve_user_by_email_with_authy(email: str):
    try:
        user = await Users.get(email=email).prefetch_related(
            Prefetch("authy", queryset=Authy.filter())            
        )

    except DoesNotExist:
        raise LoginInvalidException

    return user


@atomic()
async def update_user_last_login(user: Users):
    try:
        await user.save(update_fields=["last_login"])

    except Exception as e:
        raise e


@atomic()
async def create_authy(authy_id: int, user_id: int):
    try:
        await Authy.create(authy_id=authy_id, user_id=user_id)

    except Exception as e:
        raise e


@atomic()
async def delete_authy(authy: Authy):
    if authy is None:
        raise AuthyUnregisteredException

    try:
        authy = await Authy.get(authy_id=authy.authy_id)
        await authy.delete()

    except DoesNotExist:
        raise AuthyUnregisteredException
