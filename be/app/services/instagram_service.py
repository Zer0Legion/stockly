import requests
import time

from app.errors.external_api_error import ExternalServiceError
from app.models.request.instagram_service_request import (
    InstagramCarouselRequest,
    InstagramImageRequest,
)
from app.settings import Settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class InstagramService:
    def __init__(self):
        self.settings = Settings().get_settings()

    def _create_container(self, req: InstagramImageRequest):
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media",
            params={
                "image_url": f"{self.settings.INSTA_CONTAINER_URL_PREFIX}{req.s3_object_id}",
                "caption": req.caption,
                "access_token": self.settings.INSTA_ACCESS_TOKEN,
            },
        )
        if response:
            return response.json()
        else:
            raise ExternalServiceError("Failed to create container")

    def _publish_container(self, container_id: str):
        logger.info(f"Publishing container with ID: {container_id}")
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media_publish",
            headers={"Content-Type": "application/json"},
            params={
                "access_token": self.settings.INSTA_ACCESS_TOKEN,
                "creation_id": container_id,
            },
        )
        if response:
            return response.json()
        else:
            raise ExternalServiceError("Failed to publish container")

    def publish_image(self, req: InstagramImageRequest) -> dict | None:
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
            container = self._create_container(req)
            container_id = container.get("id")
            return self._publish_container(container_id)
        except KeyError as e:
            logger.error("Key not found in response:", e)
            logger.error("Response:", container)
            raise e
        except ExternalServiceError as e:
            logger.error("External service error:", e)
            raise e

    def publish_carousel_image(self, req: InstagramCarouselRequest) -> dict | None:
        """
        Publishes a carousel of images to instagram as a post.

        Parameters
        ----------
        reqs : list[InstagramImageRequest]
            list of image requests

        Returns
        -------
        dict | None
            the success response, or None
        """
        try:

            # Get IG container IDs
            container_ids = []
            for s3_object_id in req.s3_object_ids:
                logger.info(f"Creating container for S3 object ID: {s3_object_id}")

                try:
                    container = self._create_container(
                        InstagramImageRequest(
                            s3_object_id=s3_object_id, caption=req.caption
                        )
                    )
                    container_ids.append(container.get("id"))
                except ExternalServiceError as e:
                    logger.error(
                        f"Failed to create container for S3 object ID {s3_object_id}:",
                        e,
                    )
                    pass

            # Publish carousel container with the obtained IDs

            max_attempts = 3
            last_exc = None
            caption = req.caption

            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(
                        f"Attempt {attempt} to create carousel with containers: {container_ids}\n{caption}"
                    )
                    response = requests.post(
                        url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media",
                        headers={"Content-Type": "application/json"},
                        params={
                            "access_token": self.settings.INSTA_ACCESS_TOKEN,
                            "children": ",".join(container_ids),
                            "media_type": "CAROUSEL",
                            "caption": caption,
                        },
                    )

                    if response:
                        carousel_container = response.json()
                        carousel_container_id = carousel_container.get("id")
                        return self._publish_container(carousel_container_id)
                except Exception as e:
                    last_exc = e

                    logger.exception(
                        f"publish_carousel_image failed on attempt {attempt}: {e}\n{container_ids}\n{caption}"
                    )
                    logger.info("Retrying with empty caption")
                    caption = ""
                if attempt < max_attempts:
                    time.sleep(1)
            if last_exc:
                raise last_exc
        except KeyError as e:
            logger.error("Key not found in response:", e)
            raise e
        except ExternalServiceError as e:
            logger.error("External service error:", e)
            raise e
