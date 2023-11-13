from app.config import setting


aerich_migrate_models: list = [
    "aerich.models",
    *setting.DATABASE_MIGRATION_MODELS,
]

TORTOISE_ORM = {
    "connections": {"default": setting.DATABASE_URL},
    "apps": {
        "models": {
            "models": aerich_migrate_models,
            "default_connection": "default",
        },
    },
}