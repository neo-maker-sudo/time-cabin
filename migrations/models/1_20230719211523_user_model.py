from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "nickname" VARCHAR(64),
    "active" BOOL NOT NULL  DEFAULT True,
    "start_time" TIMESTAMPTZ,
    "end_time" TIMESTAMPTZ,
    "avatar" TEXT,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);
        DROP TABLE IF EXISTS "users";"""
