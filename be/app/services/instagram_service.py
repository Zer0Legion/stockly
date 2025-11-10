import requests

from models.request.instagram_service_request import InstagramCarouselRequest, InstagramImageRequest
from settings import Settings
from errors.external_api_error import ExternalServiceError

class InstagramService:
    def _create_container(self, req: InstagramImageRequest):
        settings = Settings().get_settings()
        response = requests.post(
            url=f"https://graph.instagram.com/v21.0/{settings.INSTA_USER_ID}/media",
            params={
                "image_url": f"{settings.INSTA_CONTAINER_URL_PREFIX}{req.s3_object_id}",
                "caption": req.caption,
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
            print("Key not found in response:", e)
            print("Response:", container)
            raise e
        except ExternalServiceError as e:
            print("External service error:", e)
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
            container_ids = []
            for s3_object_id in req.s3_object_ids:
                container = self._create_container(InstagramImageRequest(s3_object_id=s3_object_id, caption=req.caption))
                container_ids.append(container.get("id"))

            settings = Settings().get_settings()
            response = requests.post(
                url=f"https://graph.instagram.com/v21.0/{settings.INSTA_USER_ID}/media",
                headers={"Content-Type": "application/json"},
                params={
                    "access_token": settings.INSTA_ACCESS_TOKEN,
                    "children": ",".join(
                        container_ids
                    ),
                    "media_type": "CAROUSEL",
                },
            )
            if response:
                carousel_container = response.json()
                carousel_container_id = carousel_container.get("id")
                return self._publish_container(carousel_container_id)
            else:
                raise ExternalServiceError("Failed to create carousel container")
        except KeyError as e:
            print("Key not found in response:", e)
            raise e
        except ExternalServiceError as e:
            print("External service error:", e)
            raise e