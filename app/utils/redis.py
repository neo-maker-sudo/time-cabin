import aioredis
from aioredis.exceptions import ConnectionError
from app.config import setting


async def connect_redis():
    try:
        redis = aioredis.from_url(
            setting.REDIS_URL,
            decode_responses=True
        )

        await redis.ping()

    except ConnectionError as e:
        raise e

    return redis


async def set_email_verify_otp_into_redis(redis, /, *, user_id, value):
    async with redis.client() as conn:
        await conn.execute_command(
            "set",
            setting.EMAIL_VERIFICATION_KEY_FORMAT_STRING.format(user_id),
            value,
            "ex",
            setting.EMAIL_VERIFICATION_OTP_EXPIRED_SECONDS
        )


async def get_email_verify_otp_from_redis(redis, /, *, user_id):
    return await redis.get(
        setting.EMAIL_VERIFICATION_KEY_FORMAT_STRING.format(user_id),
    )


async def set_email_verify_otp_expired(redis, /, *, user_id):
    async with redis.client() as conn:
        await conn.execute_command(
            "expire",
            setting.EMAIL_VERIFICATION_KEY_FORMAT_STRING.format(user_id),
            0,
        )
