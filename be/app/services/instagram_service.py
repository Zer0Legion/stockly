from httpx import head
import requests
import time

from app.errors.external_api_error import ExternalServiceError
from app.models.request.instagram_service_request import (
    InstagramCarouselRequest,
    InstagramImageRequest,
)
from app.settings import Settings
from app.logging_config import get_logger
from app.models.response.instagram_service_response import (
    InstagramContainerStatus,
    InstagramContainerStatusCodeEnum,
    InstagramServiceContainer,
)

logger = get_logger(__name__)


class InstagramService:
    def __init__(self):
        self.settings = Settings().get_settings()

    def _create_container_from_s3(
        self, req: InstagramImageRequest
    ) -> InstagramServiceContainer:
        # Require that s3_object_id is provided
        if not req.s3_object_id:
            raise ValueError("s3_object_id must be provided in InstagramImageRequest")
        req.url = f"{self.settings.S3_CONTAINER_URL_PREFIX}{req.s3_object_id}"
        return self._create_instagram_image_container(req)

    def _create_instagram_image_container(
        self, req: InstagramImageRequest
    ) -> InstagramServiceContainer:
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media",
            headers={"Content-Type": "application/json"},
            params={
                "access_token": self.settings.INSTA_ACCESS_TOKEN,
                "image_url": req.url,
                "caption": req.caption,
            },
        )
        if response:
            return InstagramServiceContainer.model_validate(response.json())
        else:
            raise ExternalServiceError("Failed to create image container")

    def publish_container(
        self, container: InstagramServiceContainer
    ) -> InstagramServiceContainer:
        logger.info(f"Publishing container with ID: {container.id}")
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media_publish",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.INSTA_ACCESS_TOKEN}",
            },
            params={
                "creation_id": container.id,
            },
        )
        if response:
            return InstagramServiceContainer.model_validate(response.json())
        else:
            raise ExternalServiceError(
                f"Failed to publish container Errors: {response.json()}"
            )

    def publish_image(self, req: InstagramImageRequest) -> InstagramServiceContainer:
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
            if req.s3_object_id:
                container = self._create_container_from_s3(req)
            else:
                container = self._create_instagram_image_container(req)
            return self.publish_container(container)
        except KeyError as e:
            logger.error("Key not found in response:", e)
            logger.error("Response:", container)
            raise e
        except ExternalServiceError as e:
            logger.error("External service error:", e)
            raise e

    def publish_carousel_image(
        self, req: InstagramCarouselRequest
    ) -> InstagramServiceContainer:
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

            # Get IG containers
            if req.instagram_container_ids:
                containers = [
                    InstagramServiceContainer(id=container_id)
                    for container_id in req.instagram_container_ids
                ]
            else:
                containers = []
                for s3_object_id in req.s3_object_ids:
                    logger.info(f"Creating container for S3 object ID: {s3_object_id}")

                    try:
                        container = self._create_container_from_s3(
                            InstagramImageRequest(s3_object_id=s3_object_id, caption="")
                        )
                        containers.append(container)
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
            logger.info(f"caption: {caption}")
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(
                        f"Attempt {attempt} to create carousel with containers: {containers}\n{caption}"
                    )
                    response = requests.post(
                        url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.settings.INSTA_ACCESS_TOKEN}",
                        },
                        params={
                            "children": ",".join(
                                [container.id for container in containers]
                            ),
                            "media_type": "CAROUSEL",
                            "caption": caption,
                        },
                    )

                    if response:
                        carousel_container = InstagramServiceContainer.model_validate(
                            response.json()
                        )

                        while (
                            self.get_container_status(carousel_container).status_code
                            != InstagramContainerStatusCodeEnum.FINISHED
                        ):
                            logger.info("Waiting for carousel container to be ready...")
                            time.sleep(2)

                        return self.publish_container(carousel_container)
                except Exception as e:
                    last_exc = e

                    logger.exception(
                        f"publish_carousel_image failed on attempt {attempt}: {e}\n{containers}\n{caption}"
                    )
                    logger.info("Retrying with empty caption")
                    caption = "Stockly"
                if attempt < max_attempts:
                    time.sleep(1)
            if last_exc:
                raise last_exc
        except KeyError as e:
            logger.error(f"Key not found in response: {e}")
            raise e
        except ExternalServiceError as e:
            logger.error(f"External service error: {e}")
            raise e

    def create_carousel_container(
        self, ig_container_ids: list[str], caption: str
    ) -> InstagramServiceContainer:
        """
        Creates an Instagram carousel container.

        Parameters
        ----------
        ig_container_ids : list[str]
            List of Instagram container IDs.
        caption : str
            Caption for the carousel.

        Returns
        -------
        dict
            The response from Instagram API.
        """
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{self.settings.INSTA_USER_ID}/media",
            headers={"Content-Type": "application/json"},
            params={
                "access_token": self.settings.INSTA_ACCESS_TOKEN,
                "children": ",".join(ig_container_ids),
                "media_type": "CAROUSEL",
                "caption": caption,
            },
        )
        if response:
            return InstagramServiceContainer.model_validate(response.json())
        else:
            raise ExternalServiceError("Failed to create carousel container")

    def get_container_status(
        self, container: InstagramServiceContainer
    ) -> InstagramContainerStatus:
        """
        Get the status of an Instagram container.

        Parameters
        ----------
        container_id : str
            The Instagram container ID.

        Returns
        -------
        InstagramContainerStatus
            The status of the container.
        """
        response = requests.get(
            url=f"https://graph.instagram.com/v21.0/{container.id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.INSTA_ACCESS_TOKEN}",
            },
            params={
                "fields": "status_code,id,status",
            },
        )
        if response:
            data = response.json()
            return InstagramContainerStatus.model_validate(data)
        else:
            raise ExternalServiceError("Failed to get container status")
