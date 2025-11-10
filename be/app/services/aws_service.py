import uuid
import boto3

from settings import Settings
from models.response.aws_service_response import S3StorageObject
from models.request.aws_service_request import DeleteImageRequest, UploadImageRequest


class AWSService:
    """
    Service for interacting with AWS.
    """

    def __init__(self) -> None:
        settings = Settings().get_settings()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET,
            region_name=settings.AWS_REGION
        )

    def upload_file(self, param: UploadImageRequest) -> S3StorageObject:
        """
        Upload a file to an S3 bucket.

        Parameters
        ----------
        file_path : str
            path to the file
        bucket : str
            bucket name
        object_name : str
            object name

        Returns
        -------
        S3StorageObject
            s3 object
        """
        object_name = uuid.uuid4().hex
        self.s3.upload_file(param.file_path, param.bucket, object_name)

        return S3StorageObject(object_name=object_name, bucket=param.bucket)

    def delete_file(self, param: DeleteImageRequest):
        """
        Delete a file from an S3 bucket.

        Parameters
        ----------
        bucket : str
            bucket name
        object_name : str
            object name
        """
        self.s3.delete_object(Bucket=param.bucket, Key=param.object_name)
