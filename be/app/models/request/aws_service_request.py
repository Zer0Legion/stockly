from pydantic import BaseModel


class UploadImageRequest(BaseModel):
    file_path: str
    bucket: str


class DeleteImageRequest(BaseModel):
    bucket: str
    object_name: str
