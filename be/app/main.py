from http.client import HTTPException
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from contextlib import asynccontextmanager

from app.logging_config import configure_logging, get_logger
from app.routes import api_routes, dev_routes
from app.settings import MODE, Settings
from app.dependencies import get_automation_logic_singleton
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.settings import Settings


EXEMPTED_FROM_AUTH = {"/docs", "/redoc", "/openapi.json"}

# -----------------
# Security
# -----------------
bearer_scheme = HTTPBearer(auto_error=False)


def verify_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> None:
    """
    Validates the Authorization: Bearer <token> header against settings.API_BEARER_TOKEN.
    Raises 401 if missing or invalid.
    """
    # Allow unauthenticated access to docs and OpenAPI schema
    if request.url.path in EXEMPTED_FROM_AUTH or request.url.path.startswith("/dev/"):
        return

    settings = Settings().get_settings()
    expected = (settings.API_BEARER_TOKEN or "").strip()

    if not expected:
        # No token configured – reject all requests clearly
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API bearer token not configured",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    provided = (credentials.credentials or "").strip()
    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Use FastAPI lifespan to perform startup/shutdown tasks."""
    _ = get_automation_logic_singleton()
    get_logger(__name__).info("AltService singleton initialized on startup")
    yield


settings = Settings().get_settings()
app = FastAPI(dependencies=[Depends(verify_bearer_token)], lifespan=lifespan)

configure_logging(level=logging.INFO)
logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "127.0.0.1"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Allowing CORS from {settings.FRONTEND_URL} and localhost")

app.include_router(api_routes.router)

if str(settings.ENV_MODE) == MODE.DEV.value:
    logger.info("DEV mode detected; included dev_routes")
    app.include_router(dev_routes.router)
