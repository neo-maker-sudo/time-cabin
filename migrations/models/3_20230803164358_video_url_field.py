from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" ALTER COLUMN "url" DROP NOT NULL;
        ALTER TABLE "videos" ALTER COLUMN "url" TYPE TEXT USING "url"::TEXT;
        ALTER TABLE "videos" ALTER COLUMN "url" TYPE TEXT USING "url"::TEXT;
        ALTER TABLE "videos" ALTER COLUMN "url" TYPE TEXT USING "url"::TEXT;
        ALTER TABLE "videos" ALTER COLUMN "type" DROP NOT NULL;
        ALTER TABLE "videos" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" ALTER COLUMN "url" TYPE VARCHAR(256) USING "url"::VARCHAR(256);
        ALTER TABLE "videos" ALTER COLUMN "url" SET NOT NULL;
        ALTER TABLE "videos" ALTER COLUMN "url" TYPE VARCHAR(256) USING "url"::VARCHAR(256);
        ALTER TABLE "videos" ALTER COLUMN "url" TYPE VARCHAR(256) USING "url"::VARCHAR(256);
        ALTER TABLE "videos" ALTER COLUMN "type" SET NOT NULL;
        ALTER TABLE "videos" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);"""
