import time
from openai import OpenAI
from openai.types import ImagesResponse
from openai.types.responses import Response, ResponseOutputMessage
from openai.types.responses.response_output_text import ResponseOutputText
from openai.types.responses.response_output_refusal import ResponseOutputRefusal

from app.logging_config import get_logger
from app.models.request.generate_image_request import (
    GenerateImageRequest,
)
from app.settings import Settings

logger = get_logger(__name__)


class OpenAIService:
    def __init__(self):
        self.settings = Settings().get_settings()

        self.client = OpenAI(
            organization="org-DZHAxp8YdIcZZTJ305iG7cKb",
            project="proj_llL0cbSB0T4XXDSSGOvUCbdT",
            api_key=self.settings.OPENAI_API_KEY,
            max_retries=3,
        )

    def generate_written_prompt(
        self, stock_ticker: str, formatted_html: str, retry_count=0
    ) -> str:
        """
        Generate a written prompt for the stock based on the formatted HTML.
        """
        PROMPT = f"""
        I have scraped several Google News articles related to the stock {stock_ticker}. Please provide the following:

        1. A concise summary of the 3 main key points from these news articles. Prefix this with a '###' header, named "Summary:".
        2. An analysis of the sentiment (ecstatic, positive, neutral, negative, disastrous) of the articles based on how they affect the stock's outlook. Prefix this with a '###' header, named "Sentiment Analysis: <Your evaluation>".
        {formatted_html}
        """

        self.settings = Settings().get_settings()

        response: Response = self.client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": PROMPT}],
            temperature=0.7,
        )

        logger.info(f"Generated written prompt for {stock_ticker}: {response}")

        if response.output and len(response.output) > 0:
            assert type(response.output[0]) is ResponseOutputMessage
            response_output: ResponseOutputMessage = response.output[0]
            content = response_output.content[0]

            if type(content) is ResponseOutputText:
                return content.text
            else:
                assert type(content) is ResponseOutputRefusal
                output_refusal: ResponseOutputRefusal = content
                logger.error(
                    f"OpenAI refused to generate written prompt: {output_refusal.refusal}"
                )
        else:
            logger.error(f"OpenAI response has no output: {response}")

        if retry_count < 3:
            time.sleep(2**retry_count)
            return self.generate_written_prompt(
                stock_ticker, formatted_html, retry_count=retry_count + 1
            )

        return ""

    def generate_image_prompt(self, request: GenerateImageRequest, retry_count=0):
        """
        Generate an image prompt based on the text prompt.
        """

        TEMPLATE = """
        Generate an image based on the following text prompt. You may show a setting of the company that I am mentioning, and maybe show some traits specific to the company. 
        If you are about to generate an image of a person, I would prefer you to generate an executive in smartly dressed attire, 
        of different genders and races. 
        
        If possible, you are allowed to show the company logo. However, do not generate any text or numbers.

        {}

        I want to reflect the sentiment of the news articles in the image. The sentiment is {}.
        """

        self.settings = Settings().get_settings()
        prompt = TEMPLATE.format(request.text_prompt, request.sentiment.value)

        response: ImagesResponse = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

        if not response:
            logger.error(f"Error generating image")
            if retry_count < 3:
                time.sleep(2**retry_count)
                return self.generate_image_prompt(request, retry_count=retry_count + 1)
            return None

        else:
            assert response.data and len(response.data) > 0
            logger.info(f"Generated image prompt response: {response}")
            image_url = response.data[0].url
            return image_url
