import enum
from pydantic import BaseModel, Field


class InstagramContainerStatusCodeEnum(str, enum.Enum):
    """
    Enumerates possible container status codes returned by Instagram Graph API.

    
    EXPIRED — The container was not published within 24 hours and has expired.

    ERROR — The container failed to complete the publishing process.

    FINISHED — The container and its media object are ready to be published.

    IN_PROGRESS — The container is still in the publishing process.

    PUBLISHED — The container's media object has been published.
    """
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    IN_PROGRESS = "IN_PROGRESS"
    PUBLISHED = "PUBLISHED"


class InstagramContainerStatus(BaseModel):
    """Represents the status of an Instagram media container.

    """
    model_config = {"extra": "ignore"}

    status_code: InstagramContainerStatusCodeEnum = Field(..., description="Machine status code from Instagram (e.g. FINISHED, ERROR).")
    status: str = Field(..., description="Human-readable status text.")
    error_message: str = Field("", description="Present when status_code=ERROR; empty otherwise.")
    id: str = Field(..., description="Container ID.")

class InstagramServiceContainer(BaseModel):
    """Represents the response from Instagram service when creating a media container.

    """
    model_config = {"extra": "ignore"}

    id: str = Field(..., description="Container ID.")
