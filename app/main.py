
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.config import setting
from app.routes import video, users
from app.utils.general import create_videos_folder

app = FastAPI()

app.include_router(video.router)
app.include_router(users.router)

register_tortoise(
    app,
    db_url=setting.DATABASE_URL,
    modules={"models": setting.DATABASE_MIGRATION_MODELS},
)

@app.on_event("startup")
async def application_startup_event():
    create_videos_folder([
        setting.M3U8_DESTINATION_FOLDER,
        setting.MP4_DESTINATION_FOLDER,
    ])

@app.get("/")
def home_page_view():
    return {"Hello": "m3u8"}
