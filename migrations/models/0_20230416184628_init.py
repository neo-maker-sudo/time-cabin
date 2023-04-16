from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "videos" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(64) NOT NULL,
    "information" TEXT NOT NULL,
    "type" VARCHAR(10) NOT NULL,
    "url" VARCHAR(256) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "videos"."type" IS 'mp4: mp4\nmp3: mp3';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
