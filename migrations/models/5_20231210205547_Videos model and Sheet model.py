from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_videos_label_1f8567";
        CREATE TABLE IF NOT EXISTS "playlists" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(32) NOT NULL
        );;
        ALTER TABLE "videos" ADD "identifier_code" VARCHAR(255) NOT NULL;
        ALTER TABLE "videos" ADD "playlist_id" INT;
        ALTER TABLE "videos" ADD COLUMN "title" TEXT NOT NULL;
        ALTER TABLE "videos" RENAME COLUMN "information" TO "image";
        ALTER TABLE "videos" DROP COLUMN "label";
        ALTER TABLE "videos" DROP COLUMN "likes";
        ALTER TABLE "videos" DROP COLUMN "modified_at";
        ALTER TABLE "videos" DROP COLUMN "type";
        ALTER TABLE "videos" ADD CONSTRAINT "fk_videos_playlists_cc408d9a" FOREIGN KEY ("playlist_id") REFERENCES "playlists" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "videos" DROP CONSTRAINT "fk_videos_playlists_cc408d9a";
        ALTER TABLE "videos" RENAME COLUMN "image" TO "information";
        ALTER TABLE "videos" ADD "label" JSONB;
        ALTER TABLE "videos" ADD "likes" INT NOT NULL  DEFAULT 0;
        ALTER TABLE "videos" ADD "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "videos" ADD "type" VARCHAR(10);
        ALTER TABLE "videos" DROP COLUMN "title";
        ALTER TABLE "videos" DROP COLUMN "identifier_code";
        ALTER TABLE "videos" DROP COLUMN "playlist_id";
        DROP TABLE IF EXISTS "playlists";
        CREATE INDEX "idx_videos_label_1f8567" ON "videos" USING GIN ("label");;"""
