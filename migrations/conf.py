from app.config import setting


aerich_migrate_models: list = [
    "aerich.models",
    *setting.db_models,
]

TORTOISE_ORM = {
    "connections": {"default": setting.db_url},
    "apps": {
        "models": {
            "models": aerich_migrate_models,
            "default_connection": "default",
        },
    },
}