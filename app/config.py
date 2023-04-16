

class Setting:
    db_url: str = "postgres://postgres:postgres@localhost:5432/m3u8"
    db_models: list = [
        "app.models.video",
    ]

    video_model_url: str = "./static"

setting = Setting()
