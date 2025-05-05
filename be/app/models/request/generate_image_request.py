from enum import Enum

from pydantic import BaseModel


class SentimentEnum(str, Enum):
    """Enum for sentiment."""

    ECSTATIC = "ecstatic"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    DISASTROUS = "disastrous"

    

class GenerateImageRequest(BaseModel):
    text_prompt: str
    sentiment: SentimentEnum