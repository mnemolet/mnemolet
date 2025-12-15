from fastapi import FastAPI

from mnemolet.api.app import api_router
from mnemolet.ui.routes import ui_router

app = FastAPI()

# API
app.include_router(api_router, prefix="/api")

# UI
app.include_router(ui_router)
