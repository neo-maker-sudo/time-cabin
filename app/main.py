
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.config import setting
from app.routes import video

app = FastAPI()

app.include_router(video.router)

register_tortoise(
    app,
    db_url=setting.db_url,
    modules={"models": setting.db_models},
)

@app.get("/")
def home_page_view():
    return {"Hello": "m3u8"}
