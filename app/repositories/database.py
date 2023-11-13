import uuid
from abc import ABCMeta, abstractmethod
from tortoise import connections
from tortoise.transactions import atomic


class DBRepository(object, metaclass=ABCMeta):

    @abstractmethod
    def get_or_create(self):
        raise NotImplemented


class PostgreSQLRepository(DBRepository):

    def __init__(self, conn_alias):
        self.conn_alias =  conn_alias

    @atomic()
    async def get_or_create(self, model_name, object):
        conn = connections.get(self.conn_alias)

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

        qs = await conn.execute_query_dict(command, [
            str(uuid.uuid4()),
            object["email"],
            object["nickname"],
            object["email_verified"],
            object["avatar"],
        ])

        return qs[0]
