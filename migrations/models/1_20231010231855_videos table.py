from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" ADD "likes" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "videos" ADD "label" JSONB NULL;
        ALTER TABLE "videos" DROP COLUMN "name";
        CREATE INDEX "idx_videos_label_1f8567" ON "videos" USING GIN (to_tsvector('simple', label ->> 'tags'));;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_videos_label_1f8567";
        ALTER TABLE "videos" ADD "name" VARCHAR(64) NOT NULL;
        ALTER TABLE "videos" DROP COLUMN "likes";
        ALTER TABLE "videos" DROP COLUMN "label";"""
