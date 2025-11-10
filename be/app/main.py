from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import MODE, Settings
from routes import api_routes, dev_routes

app = FastAPI()
settings = Settings().get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "127.0.0.1"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_routes.router)

if settings.ENV_MODE.value == MODE.DEV.value:
    app.include_router(dev_routes.router)
