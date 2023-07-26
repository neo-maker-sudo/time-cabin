from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" ADD "user_id" INT;
        ALTER TABLE "videos" ADD CONSTRAINT "fk_videos_users_dd2a9c7e" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" DROP CONSTRAINT "fk_videos_users_dd2a9c7e";
        ALTER TABLE "videos" DROP COLUMN "user_id";"""
