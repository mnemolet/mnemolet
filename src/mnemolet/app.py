from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mnemolet.api.app import api_router
from mnemolet.ui.routes import ui_router

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "ui" / "static"),
    name="static",
)

# API
app.include_router(api_router, prefix="/api")

# UI
app.include_router(ui_router)
