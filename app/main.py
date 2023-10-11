
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from tortoise.contrib.fastapi import register_tortoise
from app.config import setting
from app.routes import video, users, auth, mainpage
from app.utils.general import create_videos_folder

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=setting.CORS_METHODS,
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=setting.TRUSTS_HOSTS)

app.include_router(video.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(mainpage.router)

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
def home_page_view(request: Request):
    return {
        "IP": request.client.host,
        "DS": setting.DOCKER_STATUS,
    }