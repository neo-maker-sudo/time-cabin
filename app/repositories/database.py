import uuid
from abc import ABCMeta, abstractmethod
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic
from app.exceptions.videos import PlaylistDoesNotExistException
from app.sql.models.video import Playlist, Videos


class AbstractDBRepository(object, metaclass=ABCMeta):

    @abstractmethod
    def get_or_create(self):
        raise NotImplemented


class PostgreSQLRepository(AbstractDBRepository):

    # if error happening will rollback transaction
    async def add_playlist_with_video(self, object: dict, playlist_name: str, connection):
        playlist = await Playlist.create(name=playlist_name)

        object.update({"playlist_id": playlist.id})
        await Videos.create(**object, using_db=connection)

    async def edit_playlist_with_video(self, object: dict, playlist_name: str, connection):
        try:
            playlist = await Playlist.get(name=playlist_name)

        except DoesNotExist:
            raise PlaylistDoesNotExistException

        object.update({"playlist_id": playlist.id})
        await Videos.create(**object, using_db=connection)

    @atomic()
    async def get_or_create(self, model_name, object: dict, connection):
        command = f"""
        with select_data as (
            SELECT id, email, nickname, email_verified, avatar
            FROM {model_name}
            WHERE email = CAST($2 AS VARCHAR)

        ), insert_data as (
            INSERT INTO {model_name}(id, email, nickname, email_verified, avatar)
            SELECT CAST($1 AS UUID), CAST($2 AS VARCHAR), $3, $4, $5
            WHERE NOT EXISTS (
                SELECT id
                FROM {model_name}
                WHERE email = CAST($2 AS VARCHAR)
            )
            RETURNING id, email, nickname, email_verified, avatar
        )

        SELECT id, email, nickname, email_verified, avatar
        FROM select_data
        UNION ALL
        SELECT id, email, nickname, email_verified, avatar
        FROM insert_data
        """

        qs = await connection.execute_query_dict(command, [
            str(uuid.uuid4()),
            object["email"],
            object["nickname"],
            object["email_verified"],
            object["avatar"],
        ])

        return qs[0]
