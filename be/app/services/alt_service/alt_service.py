from ast import literal_eval
import json
from math import e
import random

from google import genai
from google.genai import types
from PIL import Image

from app.settings import Settings
from openai import OpenAI

from app.logging_config import get_logger
from app.errors.external_api_error import ExternalServiceError
from app.models.request.aws_service_request import UploadImageRequest
from app.models.request.instagram_service_request import InstagramImageRequest
from app.services.aws_service import AWSService
from app.services.instagram_service import InstagramService
from app.services.project_io_service import ProjectIoService

logger = get_logger(__name__)


class AltService:
    def __init__(
        self,
        project_io_service: ProjectIoService,
        aws_service: AWSService,
    ):
        self.project_io_service = project_io_service
        self.aws_service = aws_service
        self.settings = Settings().get_settings()
        self.deepseek_client = OpenAI(
            api_key=self.settings.DEEPSEEK_KEY, base_url="https://api.deepseek.com"
        )
        self.CAPTION_TEMPLATES = json.loads(self.settings.CAPTION_TEMPLATES)
        self.TOP_COLOURS = literal_eval(self.settings.TOP_COLOURS)
        self.BOTTOM_COLOURS = literal_eval(self.settings.BOTTOM_COLOURS)
        self.EXTRA_PROMPT = literal_eval(self.settings.EXTRA_PROMPT)
        self.S3_OBJECTS = literal_eval(self.settings.ALT_S3_OBJECTS)

    def generate_caption(self, retry_count=0) -> str:
        caption_theme = random.choice(list(self.CAPTION_TEMPLATES.keys()))

        format_prompt = self.settings.ALT_SERVICE_CAPTION_PROMPT.format(
            caption_theme, ", ".join(self.CAPTION_TEMPLATES[caption_theme])
        )

        logger.info(f"Prompting deepseek with: {format_prompt}")
        response = self.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {
                    "role": "user",
                    "content": format_prompt,
                },
            ],
            stream=False,
        )
        if response.choices[0].message.content:
            response_text = response.choices[0].message.content.strip().lower()

            # remove period if it exists in last 10 characters
            if response_text.rfind(".") >= len(response_text) - 10:
                response_text = response_text.replace(".", "")
        else:
            if retry_count < 3:
                return self.generate_caption(retry_count + 1)
            else:
                logger.error("Failed to generate caption after 3 retries")
                raise ExternalServiceError("Failed to generate caption")
        logger.info(f"Generated caption: {response_text}")
        return response_text

    def _hit_gemini_api(self, client, prompt, example_image_filepath, retry_count=0):
        try:
            response: types.GenerateContentResponse = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt, Image.open(example_image_filepath)],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                ),
            )
            if not response or not response.parts:
                raise
            return response
        except Exception as e:
            if retry_count < 3:
                return self._hit_gemini_api(
                    client, prompt, example_image_filepath, retry_count + 1
                )
            else:
                logger.error(f"Failed to hit Gemini API after 3 retries: {e}")
                raise ExternalServiceError("Failed to generate image after retries")

    def generate_image(self, output_filepath: str = "alt_service_generated_image.png"):
        client = genai.Client(api_key=self.settings.GEMINI_KEY)

        top_colour = random.choice(self.TOP_COLOURS)
        bottom_colour = random.choice(self.BOTTOM_COLOURS)
        pose_ref = random.randint(1, 10)
        extra_prompt = random.choice(self.EXTRA_PROMPT)

        prompt = self.settings.ALT_SERVICE_IMAGE_PROMPT.format(
            top_colour, bottom_colour, extra_prompt, pose_ref
        )

        example_image_s3_object = random.choice(self.S3_OBJECTS)
        example_image_filepath = self.project_io_service.download_image(
            image_url=f"https://{self.settings.ALT_S3_BUCKET_NAME}.s3.{self.settings.AWS_REGION}.amazonaws.com/{example_image_s3_object}",
            filename=f"alt_service_example_image_{example_image_s3_object}.png",
        )

        response: types.GenerateContentResponse = self._hit_gemini_api(
            client, prompt, example_image_filepath
        )

        logger.info(f"Generated image response: {response}")
        if response.parts:
            for i, part in enumerate(response.parts):
                if part.text is not None:
                    logger.info(part.text)
                elif part.inline_data is not None:
                    image = part.as_image()
                    if image:
                        # Cleanup
                        self.project_io_service.delete_file(example_image_filepath)

                        image.save(output_filepath)
                        return output_filepath

        raise ExternalServiceError("Failed to generate image")

    def create_ig_post(self):
        caption = self.generate_caption()
        image_filepath = self.generate_image()

        image_s3_object = self.aws_service.upload_file(
            UploadImageRequest(
                file_path=image_filepath, bucket=self.settings.AWS_BUCKET_NAME
            )
        )

        logger.info("Publishing to Instagram...")

        instagram_service = InstagramService(
            user_id=self.settings.INSTA_ALT_USER_ID,
            access_token=self.settings.INSTA_ALT_ACCESS_TOKEN,
        )

        instagram_id = instagram_service.publish_image(
            InstagramImageRequest(
                s3_object_id=image_s3_object.object_name,
                caption=caption,
            )
        )

        # Cleanup
        self.project_io_service.delete_file(image_filepath)

        logger.info(f"Published Instagram post with ID: {instagram_id}")
