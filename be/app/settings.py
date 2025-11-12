import enum
import os
from pathlib import Path

from dotenv import dotenv_values, find_dotenv
from pydantic import BaseModel


class MODE(enum.Enum):
    LIVE = "live"
    DEV = "dev"


class Settings(BaseModel):
    ORG_NAME: str = "Stockly"

    # Endpoints
    BACKEND_URL: str = "0.0.0.0"
    FRONTEND_URL: str = "https://stockly-six.vercel.app/"

    # Sending emails
    EMAIL_ADDRESS: str = "EMAIL_ADDRESS"
    EMAIL_PASSWORD: str = "EMAIL_PASSWORD"

    # Briefing email
    CONTENT_PREFIX: str = "Dear {},\n\nGood morning from all of us at {}! Here is our curated summary for you:\n\n# Report of your selected stocks:\n\n"

    # OpenAI
    OPENAI_API_KEY: str = "OPENAI_API_KEY"
    OPENAI_URL: str = "https://api.openai.com/v1/chat/completions"

    # Instagram
    INSTA_USER_ID: str = "user"
    INSTA_ACCESS_TOKEN: str = "token"
    INSTA_CONTAINER_URL_PREFIX: str = (
        "https://stockly-bendover.s3.us-east-1.amazonaws.com/"
    )

    # Mode: 'live' or 'dev' - controls dev-only routes/features
    ENV_MODE: str = MODE.LIVE.value

    URL_NEWS: str = "https://news.google.com/search?q="
    URL_STOCKS: str = "https://www.google.com/finance/quote/"

    TNC_EFFECTIVE_DATE: str = "2024-01-01"

    AWS_BUCKET_NAME: str = "stockly-bendover"
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET: str = ""
    AWS_REGION: str = "us-east-1"

    DEEPSEEK_KEY: str = ""
    GEMINI_KEY: str = ""

    def get_settings(self) -> "Settings":
        """
        Load configuration with the following precedence (highest last):
        1) Code defaults (class attributes)
        2) .env file values (if present)
        3) Environment variables from the OS (Render dashboard, container env)
        """
        # 1) keep code defaults already on self

        # 2) merge .env (if available) using a robust lookup
        env_path = find_dotenv(usecwd=True)
        if not env_path:
            # fallback to repo root relative to this file
            env_path = str(Path(__file__).resolve().parents[1] / ".env")
        try:
            if env_path and Path(env_path).exists():
                for key, value in dotenv_values(env_path).items():
                    if value is None:
                        continue
                    try:
                        setattr(self, key, value)
                    except Exception:
                        # ignore unknown fields
                        pass
        except Exception:
            # don't fail settings if dotenv parsing has issues
            pass

        # 3) overlay OS environment variables (highest precedence)
        for key, value in os.environ.items():
            if value in (None, ""):
                continue
            try:
                setattr(self, key, value)
            except Exception:
                pass
        return self
