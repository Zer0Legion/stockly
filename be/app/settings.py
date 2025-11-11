import enum

from dotenv import dotenv_values
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
        config = {**dotenv_values("./.env")}
        for key, value in config.items():
            try:
                setattr(self, key, value)
            except Exception as e:
                print(f"Error setting attribute {key}: {e}")
        return self
