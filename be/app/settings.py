import enum
from dotenv import dotenv_values
from pydantic import BaseModel

class MODE(enum.Enum):
    LIVE = "live"
    DEV = "dev"

class Settings(BaseModel):
    ORG_NAME: str = "Stockly"

    # Endpoints
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

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

    # Mode: 'live' or 'dev' - controls dev-only routes/features
    ENV_MODE: MODE = MODE.LIVE

    URL_NEWS: str = "https://news.google.com/search?q="
    URL_STOCKS: str = "https://www.google.com/finance/quote/"

    TNC_EFFECTIVE_DATE: str = "2024-01-01"

    def get_settings(self) -> "Settings":
        config = {**dotenv_values("./.env")}
        for key, value in config.items():
            setattr(self, key, value)
        return self
