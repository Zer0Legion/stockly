import requests

from settings import Settings
from errors.external_api_error import ExternalServiceError


class InstagramService:
    def _create_container(self, url: str, caption: str = ""):
        settings = Settings().get_settings()
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{settings.INSTA_USER_ID}/media",
            params={
                "image_url": url,
                "caption": caption,
                "access_token": settings.INSTA_ACCESS_TOKEN,
            },
        )
        if response:
            return response.json()
        else:
            raise ExternalServiceError("Failed to create container")

    def _publish_container(self, container_id: str):
        settings = Settings().get_settings()
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{settings.INSTA_USER_ID}/media_publish",
            headers={"Content-Type": "application/json"},
            params={
                "access_token": settings.INSTA_ACCESS_TOKEN,
                "creation_id": container_id,
            },
        )
        if response:
            return response.json()
        else:
            raise ExternalServiceError("Failed to publish container")

    def publish_image(self, url: str, caption: str = "") -> dict | None:
        """
        Publishes an image to instagram as a post.

        Parameters
        ----------
        url : str
            the url of the publicly hosted image
        caption : str, optional
            caption, by default ""

        Returns
        -------
        dict | None
            the success response, or None
        """
        try:
            container = self._create_container(url, caption)
            container_id = container.get("id")
            return self._publish_container(container_id)
        except KeyError as e:
            print("Key not found in response:", e)
            print("Response:", container)
            return None
        except ExternalServiceError as e:
            print("External service error:", e)
            return None


instagram_service = InstagramService()
container = instagram_service.publish_image(
    "http://127.0.0.1:8000/instagram_image?url=https%3A%2F%2Fstockly-bendover.s3.us-east-1.amazonaws.com%2F4f7455028d904ee2bd1c86965b1922ad"
)
print(container)
