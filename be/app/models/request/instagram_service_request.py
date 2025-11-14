from pydantic import BaseModel


class InstagramImageRequest(BaseModel):
    s3_object_id: str
    caption: str = ""

class InstagramCarouselRequest(BaseModel):
    s3_object_ids: list[str]
    instagram_container_ids: list[str] = []
    caption: str = ""
