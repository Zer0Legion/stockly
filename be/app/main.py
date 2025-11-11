import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# centralized logging configuration
from app.logging_config import configure_logging, get_logger
from app.routes import api_routes, dev_routes
from app.settings import MODE, Settings

settings = Settings().get_settings()
app = FastAPI()

configure_logging(level=logging.DEBUG)
logger = get_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "127.0.0.1"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_routes.router)

if str(settings.ENV_MODE) == MODE.DEV.value:
    logger.info("DEV mode detected; included dev_routes")
    app.include_router(dev_routes.router)
