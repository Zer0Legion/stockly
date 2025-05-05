from pydantic import BaseModel


class S3StorageObject(BaseModel):
    object_name: str
    bucket: str

    @property
    def url(self) -> str:
        return f"https://{self.bucket}.s3.us-east-1.amazonaws.com/{self.object_name}"
