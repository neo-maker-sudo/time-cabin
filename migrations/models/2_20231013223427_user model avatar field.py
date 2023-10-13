from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_videos_label_1f8567";
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE VARCHAR(255) USING "avatar"::VARCHAR(255);
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE VARCHAR(255) USING "avatar"::VARCHAR(255);
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE VARCHAR(255) USING "avatar"::VARCHAR(255);
        CREATE INDEX "idx_videos_label_1f8567" ON "videos" USING GIN ("label");;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_videos_label_1f8567";
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE TEXT USING "avatar"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE TEXT USING "avatar"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "avatar" TYPE TEXT USING "avatar"::TEXT;
        CREATE INDEX "idx_videos_label_1f8567" ON "videos" USING GIN ("label");;"""
