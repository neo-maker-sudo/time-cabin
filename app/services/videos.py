from tortoise.transactions import in_transaction
from app.repositories.database import PostgreSQLRepository


async def add_video(repo: PostgreSQLRepository, playlist_name: str, object: dict) -> None:
    async with in_transaction() as connection: 
        await repo.add_playlist_with_video(
            object,
            playlist_name=playlist_name,
            connection=connection
        )

async def edit_video(repo: PostgreSQLRepository, playlist_name: str, object: dict) -> None:
    async with in_transaction() as connection: 
        await repo.edit_playlist_with_video(
            object,
            playlist_name=playlist_name,
            connection=connection
        )