from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "password" DROP NOT NULL;
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE TEXT USING "avatar"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "password" SET NOT NULL;
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE VARCHAR(255) USING "avatar"::VARCHAR(255);"""
