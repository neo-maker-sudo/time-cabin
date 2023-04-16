
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home_page_view():
    return {"Hello": "m3u8"}